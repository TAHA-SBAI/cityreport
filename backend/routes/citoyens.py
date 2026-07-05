from flask import Blueprint, request, jsonify
from models import Citoyen
from ._db import get_session

bp = Blueprint("citoyens", __name__, url_prefix="/api/citoyens")


@bp.get("")
def lister():
    session = get_session()
    citoyens = session.query(Citoyen).order_by(Citoyen.nom).all()
    return jsonify([c.to_dict() for c in citoyens])


@bp.post("")
def creer():
    session = get_session()
    data = request.get_json(silent=True) or {}
    c = Citoyen(
        nom=data.get("nom", ""),
        prenom=data.get("prenom", ""),
        email=data.get("email", ""),
        telephone=data.get("telephone", ""),
    )
    session.add(c)
    session.commit()
    return jsonify(c.to_dict()), 201
