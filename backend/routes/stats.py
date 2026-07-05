from collections import defaultdict
from datetime import datetime
from flask import Blueprint, jsonify

from sqlalchemy import func
from models import Signalement, Citoyen, Agent
from ._db import get_session

bp = Blueprint("stats", __name__, url_prefix="/api/stats")


@bp.get("/overview")
def overview():
    """KPIs du dashboard général."""
    session = get_session()
    total = session.query(Signalement).count()
    resolus = session.query(Signalement).filter_by(statut="Résolu").count()
    en_cours = session.query(Signalement).filter_by(statut="En cours").count()
    nouveaux = session.query(Signalement).filter_by(statut="Nouveau").count()
    suspects = (
        session.query(Signalement)
        .join(Signalement.resultat_ml)
        .filter_by(is_anomalie=True)
        .count()
    )
    nb_citoyens = session.query(Citoyen).count()
    nb_agents = session.query(Agent).count()

    taux = round(100 * resolus / total, 1) if total else 0.0

    return jsonify({
        "total": total,
        "resolus": resolus,
        "en_cours": en_cours,
        "nouveaux": nouveaux,
        "suspects": suspects,
        "nb_citoyens": nb_citoyens,
        "nb_agents": nb_agents,
        "taux_resolution": taux,
    })


@bp.get("/par-categorie")
def par_categorie():
    session = get_session()
    rows = (
        session.query(Signalement.categorie, func.count(Signalement.id))
        .group_by(Signalement.categorie)
        .all()
    )
    return jsonify([{"categorie": c or "Inconnue", "total": n} for c, n in rows])


@bp.get("/par-statut")
def par_statut():
    session = get_session()
    rows = (
        session.query(Signalement.statut, func.count(Signalement.id))
        .group_by(Signalement.statut)
        .all()
    )
    return jsonify([{"statut": s, "total": n} for s, n in rows])


@bp.get("/par-mois")
def par_mois():
    """Évolution mensuelle du nombre de signalements."""
    session = get_session()
    signalements = session.query(Signalement).all()
    compteur = defaultdict(int)
    for s in signalements:
        cle = s.date_creation.strftime("%Y-%m")
        compteur[cle] += 1
    series = [{"mois": k, "total": v} for k, v in sorted(compteur.items())]
    return jsonify(series)


@bp.get("/par-jour")
def par_jour():
    """Volume de signalements par jour (30 derniers jours présents)."""
    session = get_session()
    signalements = session.query(Signalement).all()
    compteur = defaultdict(int)
    for s in signalements:
        cle = s.date_creation.strftime("%Y-%m-%d")
        compteur[cle] += 1
    series = [{"jour": k, "total": v} for k, v in sorted(compteur.items())]
    return jsonify(series[-30:])


@bp.get("/par-quartier")
def par_quartier():
    """Statistiques détaillées par quartier avec score de priorité agrégé."""
    session = get_session()
    signalements = session.query(Signalement).all()

    data = defaultdict(lambda: {"total": 0, "resolus": 0, "en_cours": 0})
    for s in signalements:
        q = s.quartier or "Autre"
        data[q]["total"] += 1
        if s.statut == "Résolu":
            data[q]["resolus"] += 1
        elif s.statut == "En cours":
            data[q]["en_cours"] += 1

    resultat = []
    for quartier, d in data.items():
        taux = round(100 * d["resolus"] / d["total"], 1) if d["total"] else 0
        # Score de priorité : volume élevé + faible taux de résolution = priorité
        score = round(d["total"] * (1 - taux / 100) + d["en_cours"] * 2, 1)
        resultat.append({
            "quartier": quartier,
            "total": d["total"],
            "resolus": d["resolus"],
            "en_cours": d["en_cours"],
            "taux_resolution": taux,
            "score_priorite": score,
        })
    resultat.sort(key=lambda r: r["score_priorite"], reverse=True)
    return jsonify(resultat)
