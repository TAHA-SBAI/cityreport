from datetime import datetime
from flask import Blueprint, request, jsonify

from models import Signalement, ResultatML
from ml.classifier import classifier
from ml.anomaly import detecter
from ._db import get_session

bp = Blueprint("signalements", __name__, url_prefix="/api/signalements")


@bp.get("")
def lister():
    """Liste paginée + filtres : ?categorie=&statut=&quartier=&q=&page=&limit="""
    session = get_session()
    query = session.query(Signalement)

    categorie = request.args.get("categorie")
    statut = request.args.get("statut")
    quartier = request.args.get("quartier")
    recherche = request.args.get("q")

    if categorie:
        query = query.filter(Signalement.categorie == categorie)
    if statut:
        query = query.filter(Signalement.statut == statut)
    if quartier:
        query = query.filter(Signalement.quartier == quartier)
    if recherche:
        like = f"%{recherche}%"
        query = query.filter(
            Signalement.titre.ilike(like) | Signalement.description.ilike(like)
        )

    total = query.count()
    page = max(1, int(request.args.get("page", 1)))
    limit = min(200, int(request.args.get("limit", 50)))
    items = (
        query.order_by(Signalement.date_creation.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return jsonify({
        "total": total,
        "page": page,
        "limit": limit,
        "items": [s.to_dict() for s in items],
    })


@bp.get("/<int:sid>")
def detail(sid):
    session = get_session()
    s = session.get(Signalement, sid)
    if not s:
        return jsonify({"error": "Signalement introuvable"}), 404
    return jsonify(s.to_dict())


@bp.post("")
def creer():
    """
    Crée un signalement. La catégorie est prédite automatiquement par le module
    ML, puis la détection d'anomalies est recalculée sur l'ensemble.
    """
    session = get_session()
    data = request.get_json(silent=True) or {}

    for champ in ("titre", "latitude", "longitude", "citoyen_id"):
        if champ not in data:
            return jsonify({"error": f"Champ requis manquant : {champ}"}), 400

    # Classification automatique
    categorie, score = classifier(data["titre"], data.get("description", ""))

    s = Signalement(
        titre=data["titre"],
        description=data.get("description", ""),
        photo_url=data.get("photo_url", ""),
        latitude=float(data["latitude"]),
        longitude=float(data["longitude"]),
        quartier=data.get("quartier", ""),
        statut="Nouveau",
        categorie=categorie,
        score_confiance=score,
        citoyen_id=int(data["citoyen_id"]),
        agent_id=data.get("agent_id"),
        date_creation=datetime.utcnow(),
    )
    session.add(s)
    session.commit()

    # Recalcule la détection d'anomalies sur l'ensemble (volume modéré)
    _recalculer_anomalies(session)
    session.refresh(s)

    return jsonify(s.to_dict()), 201


@bp.put("/<int:sid>")
def modifier(sid):
    session = get_session()
    s = session.get(Signalement, sid)
    if not s:
        return jsonify({"error": "Signalement introuvable"}), 404

    data = request.get_json(silent=True) or {}
    ancien_statut = s.statut

    for champ in ("titre", "description", "statut", "quartier", "agent_id"):
        if champ in data:
            setattr(s, champ, data[champ])

    # Trace le changement de statut dans la timeline
    if "statut" in data and data["statut"] != ancien_statut:
        from models import HistoriqueStatut
        session.add(HistoriqueStatut(
            signalement_id=s.id,
            ancien_statut=ancien_statut,
            nouveau_statut=data["statut"],
            commentaire=data.get("commentaire", "Statut mis à jour par un agent"),
        ))

    session.commit()
    return jsonify(s.to_dict())


@bp.delete("/<int:sid>")
def supprimer(sid):
    session = get_session()
    s = session.get(Signalement, sid)
    if not s:
        return jsonify({"error": "Signalement introuvable"}), 404
    session.delete(s)
    session.commit()
    return jsonify({"ok": True})


def _recalculer_anomalies(session):
    signalements = session.query(Signalement).all()
    resultats = detecter(signalements)
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
    session.commit()
