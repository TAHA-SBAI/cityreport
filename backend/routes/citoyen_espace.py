"""
Espace citoyen : inscription, connexion, création et suivi de ses propres
signalements, avec historique de statut (timeline).

L'authentification est volontairement simple (mot de passe stocké haché en
SHA-256) pour rester lisible dans un contexte de PFA. En production on
utiliserait bcrypt/argon2 + JWT, comme indiqué dans les perspectives du rapport.
"""

import hashlib
from datetime import datetime, date

from flask import Blueprint, request, jsonify

from models import Citoyen, Signalement, HistoriqueStatut
from ml.classifier import classifier
from ml.anomaly import detecter
from ._db import get_session

bp = Blueprint("citoyen_espace", __name__, url_prefix="/api/citoyen")


def _hash(mdp: str) -> str:
    return hashlib.sha256(mdp.encode("utf-8")).hexdigest()


@bp.post("/inscription")
def inscription():
    session = get_session()
    data = request.get_json(silent=True) or {}

    for champ in ("nom", "prenom", "email", "mot_de_passe"):
        if not data.get(champ):
            return jsonify({"error": f"Champ requis : {champ}"}), 400

    existe = session.query(Citoyen).filter_by(email=data["email"]).first()
    if existe:
        return jsonify({"error": "Cet email est déjà utilisé"}), 409

    c = Citoyen(
        nom=data["nom"],
        prenom=data["prenom"],
        email=data["email"],
        telephone=data.get("telephone", ""),
        mot_de_passe=_hash(data["mot_de_passe"]),
        date_inscription=date.today(),
    )
    session.add(c)
    session.commit()

    return jsonify({
        "ok": True,
        "citoyen": {"id": c.id, "nom": c.nom, "prenom": c.prenom, "email": c.email},
    }), 201


@bp.post("/connexion")
def connexion():
    session = get_session()
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    mdp = data.get("mot_de_passe", "")

    c = session.query(Citoyen).filter_by(email=email).first()
    if not c or c.mot_de_passe != _hash(mdp):
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    return jsonify({
        "ok": True,
        "citoyen": {
            "id": c.id, "nom": c.nom, "prenom": c.prenom, "email": c.email,
            "telephone": c.telephone,
        },
    })


@bp.get("/<int:cid>/signalements")
def mes_signalements(cid):
    session = get_session()
    signalements = (
        session.query(Signalement)
        .filter_by(citoyen_id=cid)
        .order_by(Signalement.date_creation.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in signalements])


@bp.post("/<int:cid>/signalements")
def creer_signalement(cid):
    """Le citoyen crée un signalement ; classification IA immédiate."""
    session = get_session()
    citoyen = session.get(Citoyen, cid)
    if not citoyen:
        return jsonify({"error": "Citoyen introuvable"}), 404

    data = request.get_json(silent=True) or {}
    for champ in ("titre", "latitude", "longitude"):
        if champ not in data or data[champ] in (None, ""):
            return jsonify({"error": f"Champ requis : {champ}"}), 400

    categorie, score = classifier(data["titre"], data.get("description", ""))

    s = Signalement(
        titre=data["titre"],
        description=data.get("description", ""),
        photo_url=data.get("photo_url", ""),
        latitude=float(data["latitude"]),
        longitude=float(data["longitude"]),
        quartier=data.get("quartier", ""),
        statut="Nouveau",
        urgence=data.get("urgence", ""),
        categorie=categorie,
        score_confiance=score,
        citoyen_id=cid,
        date_creation=datetime.utcnow(),
    )
    session.add(s)
    session.commit()

    # Première entrée de timeline
    session.add(HistoriqueStatut(
        signalement_id=s.id,
        ancien_statut="",
        nouveau_statut="Nouveau",
        commentaire="Signalement créé par le citoyen",
    ))
    session.commit()

    # Recalcule la détection d'anomalies
    signalements = session.query(Signalement).all()
    resultats = detecter(signalements)
    from models import ResultatML
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
    session.refresh(s)

    return jsonify(s.to_dict()), 201


@bp.get("/signalement/<int:sid>/timeline")
def timeline(sid):
    """Historique des statuts d'un signalement pour affichage en timeline."""
    session = get_session()
    entrees = (
        session.query(HistoriqueStatut)
        .filter_by(signalement_id=sid)
        .order_by(HistoriqueStatut.date_changement.asc())
        .all()
    )
    return jsonify([e.to_dict() for e in entrees])
