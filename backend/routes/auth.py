from flask import Blueprint, request, jsonify

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Authentification de démonstration (à remplacer par JWT/OAuth2 en production,
# comme indiqué dans les perspectives du rapport).
DEMO_USER = {"email": "admin@cityreport.ma", "password": "admin", "nom": "Administrateur"}


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    if email == DEMO_USER["email"] and password == DEMO_USER["password"]:
        return jsonify({
            "ok": True,
            "token": "demo-token-cityreport",
            "user": {"email": email, "nom": DEMO_USER["nom"], "role": "admin"},
        })
    return jsonify({"ok": False, "error": "Identifiants incorrects"}), 401
