from flask import Blueprint, request, jsonify
from ml.assistant import repondre, SUGGESTIONS

bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


@bp.get("/suggestions")
def suggestions():
    """Questions proposées au démarrage du chat."""
    return jsonify({"suggestions": SUGGESTIONS})


@bp.post("/message")
def message():
    """Reçoit une question et renvoie la réponse de l'assistant."""
    data = request.get_json(silent=True) or {}
    question = data.get("message", "")
    if not question.strip():
        return jsonify({"error": "Message vide"}), 400
    resultat = repondre(question)
    return jsonify(resultat)
