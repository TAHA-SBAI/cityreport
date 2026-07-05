"""
Détection des signalements suspects ou en doublon — Isolation Forest.

Le modèle apprend la distribution normale des signalements à partir de
caractéristiques dérivées :
  - position géographique (latitude, longitude)
  - heure de la journée et jour
  - densité locale : nombre de signalements proches dans le temps et l'espace
    émis par le même citoyen (détection des rafales / doublons)

Les points isolés (rares, atypiques) sont marqués comme anomalies. On distingue
ensuite la cause dominante (localisation vs fréquence) pour l'afficher à l'agent.

Usage CLI :
    python -m ml.anomaly --retrain     # recalcule pour toute la base
"""

import math
from datetime import datetime

import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    _SKLEARN = True
except ImportError:  # pragma: no cover
    _SKLEARN = False


def _haversine(lat1, lon1, lat2, lon2):
    """Distance approximative en mètres entre deux points GPS."""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _features(signalements):
    """
    Construit la matrice de caractéristiques (n, 5) :
    [lat, lon, heure, voisins_proches, signalements_meme_citoyen_24h]
    """
    rows = []
    meta = []
    for s in signalements:
        dt = s.date_creation
        heure = dt.hour + dt.minute / 60.0

        # Voisins dans un rayon de 50 m
        proches = 0
        for autre in signalements:
            if autre.id == s.id:
                continue
            d = _haversine(s.latitude, s.longitude, autre.latitude, autre.longitude)
            if d < 50:
                proches += 1

        # Signalements du même citoyen dans une fenêtre de 24 h
        rafale = 0
        for autre in signalements:
            if autre.id == s.id or autre.citoyen_id != s.citoyen_id:
                continue
            delta = abs((autre.date_creation - dt).total_seconds())
            if delta < 24 * 3600:
                rafale += 1

        rows.append([s.latitude, s.longitude, heure, proches, rafale])
        meta.append({"proches": proches, "rafale": rafale})
    return np.array(rows, dtype=float), meta


def detecter(signalements, contamination=0.06):
    """
    Entraîne un Isolation Forest sur l'ensemble fourni et renvoie, pour chaque
    signalement, un dictionnaire de résultat ML.

    Retourne : { signalement_id: {is_anomalie, score_anomalie,
                 anomalie_localisation, anomalie_frequence, raison_principale} }
    """
    if not signalements:
        return {}

    X, meta = _features(signalements)
    resultats = {}

    if _SKLEARN and len(signalements) >= 8:
        model = IsolationForest(
            n_estimators=120,
            contamination=contamination,
            random_state=42,
        )
        model.fit(X)
        preds = model.predict(X)          # -1 = anomalie, 1 = normal
        raw = model.score_samples(X)      # plus bas = plus anormal
        # Normalisation du score d'anomalie entre 0 (normal) et 1 (très suspect)
        lo, hi = raw.min(), raw.max()
        span = (hi - lo) or 1.0
        scores = [(hi - v) / span for v in raw]
    else:
        # Repli sans scikit-learn : règles simples (fenêtre/densité)
        preds = []
        scores = []
        for m in meta:
            suspect = m["proches"] >= 3 or m["rafale"] >= 3
            preds.append(-1 if suspect else 1)
            scores.append(min(1.0, (m["proches"] + m["rafale"]) / 6))

    for s, pred, score, m in zip(signalements, preds, scores, meta):
        is_anom = pred == -1
        anom_loc = m["proches"] >= 3
        anom_freq = m["rafale"] >= 3

        if anom_loc and anom_freq:
            raison = "Rafale depuis une même position"
        elif anom_loc:
            raison = "Concentration anormale au même endroit"
        elif anom_freq:
            raison = "Signalements répétés du même citoyen"
        elif is_anom:
            raison = "Coordonnées ou horaire atypiques"
        else:
            raison = ""

        resultats[s.id] = {
            "is_anomalie": bool(is_anom),
            "score_anomalie": round(float(score), 3),
            "anomalie_localisation": bool(anom_loc),
            "anomalie_frequence": bool(anom_freq),
            "raison_principale": raison,
        }
    return resultats


def _retrain_all():
    """Recalcule les résultats ML pour tous les signalements de la base."""
    import config
    from database import init_engine, Base
    from models import Signalement, ResultatML

    _, Session = init_engine(config.Config.SQLALCHEMY_DATABASE_URI)
    session = Session()

    signalements = session.query(Signalement).all()
    print(f"Analyse de {len(signalements)} signalements...")
    resultats = detecter(signalements)

    n_anom = 0
    for sid, res in resultats.items():
        rml = session.query(ResultatML).filter_by(signalement_id=sid).first()
        if not rml:
            rml = ResultatML(signalement_id=sid)
            session.add(rml)
        rml.is_anomalie = res["is_anomalie"]
        rml.score_anomalie = res["score_anomalie"]
        rml.anomalie_localisation = res["anomalie_localisation"]
        rml.anomalie_frequence = res["anomalie_frequence"]
        rml.raison_principale = res["raison_principale"]
        if res["is_anomalie"]:
            n_anom += 1

    session.commit()
    print(f"Terminé : {n_anom} signalements suspects détectés.")


if __name__ == "__main__":
    import sys
    if "--retrain" in sys.argv:
        _retrain_all()
    else:
        print("Usage : python -m ml.anomaly --retrain")
