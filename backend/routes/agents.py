from flask import Blueprint, request, jsonify
from models import Agent, Signalement
from ._db import get_session

bp = Blueprint("agents", __name__, url_prefix="/api/agents")


@bp.get("")
def lister():
    session = get_session()
    agents = session.query(Agent).order_by(Agent.nom).all()
    return jsonify([a.to_dict() for a in agents])


@bp.get("/<int:aid>")
def detail(aid):
    session = get_session()
    a = session.get(Agent, aid)
    if not a:
        return jsonify({"error": "Agent introuvable"}), 404
    data = a.to_dict()
    data["signalements"] = [s.to_dict() for s in a.signalements]
    return jsonify(data)


@bp.post("")
def creer():
    session = get_session()
    data = request.get_json(silent=True) or {}
    a = Agent(
        nom=data.get("nom", ""),
        prenom=data.get("prenom", ""),
        email=data.get("email", ""),
        telephone=data.get("telephone", ""),
        secteur=data.get("secteur", ""),
    )
    session.add(a)
    session.commit()
    return jsonify(a.to_dict()), 201


@bp.get("/assignations")
def assignations():
    """Vue consolidée : signalements regroupés par agent."""
    session = get_session()
    signalements = (
        session.query(Signalement)
        .filter(Signalement.agent_id.isnot(None))
        .all()
    )
    return jsonify([
        {
            "signalement_id": s.id,
            "categorie": s.categorie,
            "quartier": s.quartier,
            "agent": f"{s.agent.prenom} {s.agent.nom}" if s.agent else None,
            "secteur": s.agent.secteur if s.agent else None,
            "statut": s.statut,
        }
        for s in signalements
    ])
