from flask import Blueprint, jsonify
from models import Signalement, ResultatML
from ._db import get_session

bp = Blueprint("ml", __name__, url_prefix="/api/ml")


@bp.get("/suspects")
def suspects():
    """Top des signalements suspects, triés par score d'anomalie décroissant."""
    session = get_session()
    rows = (
        session.query(Signalement)
        .join(Signalement.resultat_ml)
        .filter(ResultatML.is_anomalie.is_(True))
        .all()
    )
    rows.sort(key=lambda s: s.resultat_ml.score_anomalie, reverse=True)

    resultat = []
    for s in rows[:10]:
        r = s.resultat_ml
        resultat.append({
            "signalement_id": s.id,
            "titre": s.titre,
            "quartier": s.quartier,
            "categorie": s.categorie,
            "score_anomalie": round(r.score_anomalie, 3),
            "anomalie_localisation": r.anomalie_localisation,
            "anomalie_frequence": r.anomalie_frequence,
            "anomalie_both": r.anomalie_localisation and r.anomalie_frequence,
            "raison_principale": r.raison_principale,
        })
    return jsonify(resultat)


@bp.get("/normaux")
def normaux():
    """Signalements jugés normaux par le module de détection."""
    session = get_session()
    rows = (
        session.query(Signalement)
        .outerjoin(Signalement.resultat_ml)
        .all()
    )
    normaux = [
        s.to_dict()
        for s in rows
        if not (s.resultat_ml and s.resultat_ml.is_anomalie)
    ]
    return jsonify(normaux)


@bp.get("/classification")
def classification():
    """Répartition des signalements par catégorie prédite + métriques."""
    session = get_session()
    signalements = session.query(Signalement).all()

    from collections import defaultdict
    data = defaultdict(lambda: {"total": 0, "resolus": 0, "conf_sum": 0.0})
    for s in signalements:
        c = s.categorie or "Inconnue"
        data[c]["total"] += 1
        data[c]["conf_sum"] += s.score_confiance
        if s.statut == "Résolu":
            data[c]["resolus"] += 1

    resultat = []
    for cat, d in data.items():
        taux = round(100 * d["resolus"] / d["total"], 1) if d["total"] else 0
        conf = round(d["conf_sum"] / d["total"], 3) if d["total"] else 0
        resultat.append({
            "categorie": cat,
            "total": d["total"],
            "taux_resolution": taux,
            "confiance_moyenne": conf,
        })
    resultat.sort(key=lambda r: r["total"], reverse=True)
    return jsonify(resultat)


@bp.get("/modele")
def modele_info():
    """Informations sur le modèle de classification entraîné."""
    import os
    from ml.classifier import source_active

    info = {"source": source_active()}

    # Métadonnées du modèle si disponible
    try:
        import joblib
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "ml", "model.joblib"
        )
        if os.path.exists(model_path):
            data = joblib.load(model_path)
            info["modele"] = data.get("modele")
            info["accuracy_test"] = round(data.get("accuracy_test", 0), 4)
            info["classes"] = data.get("classes")
    except Exception:
        pass

    # Contenu du rapport d'évaluation si présent
    try:
        rapport_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "ml", "rapport_modele.txt"
        )
        if os.path.exists(rapport_path):
            with open(rapport_path, encoding="utf-8") as f:
                info["rapport"] = f.read()
    except Exception:
        pass

    return jsonify(info)
