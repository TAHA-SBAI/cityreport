import csv
import io
from flask import Blueprint, Response
from models import Signalement, Citoyen, Agent
from ._db import get_session

bp = Blueprint("export", __name__, url_prefix="/api/export")


def _csv_response(rows, header, filename):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@bp.get("/signalements.csv")
def export_signalements():
    session = get_session()
    rows = [
        [s.id, s.titre, s.categorie, s.quartier,
         s.date_creation.strftime("%Y-%m-%d"), s.statut]
        for s in session.query(Signalement).all()
    ]
    return _csv_response(
        rows,
        ["ID", "Titre", "Catégorie", "Quartier", "Date", "Statut"],
        "signalements.csv",
    )


@bp.get("/citoyens.csv")
def export_citoyens():
    session = get_session()
    rows = [
        [c.id, c.nom, c.prenom, c.email, c.telephone, len(c.signalements)]
        for c in session.query(Citoyen).all()
    ]
    return _csv_response(
        rows,
        ["ID", "Nom", "Prénom", "Email", "Téléphone", "Nb signalements"],
        "citoyens.csv",
    )


@bp.get("/agents.csv")
def export_agents():
    session = get_session()
    rows = [
        [a.id, a.nom, a.prenom, a.email, a.secteur, len(a.signalements)]
        for a in session.query(Agent).all()
    ]
    return _csv_response(
        rows,
        ["ID", "Nom", "Prénom", "Email", "Secteur", "Nb signalements gérés"],
        "agents.csv",
    )
