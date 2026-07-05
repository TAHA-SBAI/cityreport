"""
Génère une base CityReport peuplée de données fictives réalistes.

Centrée sur Fès (Maroc). Crée citoyens, agents, catégories et un historique de
signalements sur plusieurs mois, puis lance la classification et la détection
d'anomalies. On injecte volontairement quelques rafales et doublons pour que le
module ML ait des cas suspects à détecter.

Usage : python seed.py
"""

import random
from datetime import datetime, timedelta, date

import config
from database import Base, init_engine
from models import Citoyen, Agent, Categorie, Signalement, ResultatML
from ml.classifier import classifier
from ml.anomaly import detecter

random.seed(42)

# Centre de Fès + quartiers réels avec coordonnées approximatives
QUARTIERS = {
    "Fès Médina": (34.0640, -4.9770),
    "Agdal": (34.0331, -5.0000),
    "Saiss": (34.0150, -4.9900),
    "Narjiss": (34.0420, -4.9550),
    "Ville Nouvelle": (34.0370, -5.0040),
    "Zouagha": (34.0550, -5.0200),
    "Montfleuri": (34.0290, -4.9830),
}

PRENOMS = ["Youssef", "Fatima", "Mehdi", "Sara", "Khalid", "Imane", "Omar",
           "Salma", "Hamza", "Nawal", "Amine", "Rim", "Yassine", "Houda",
           "Karim", "Leila", "Tarik", "Asma", "Reda", "Soukaina"]
NOMS = ["Alaoui", "Bennani", "Cherkaoui", "Tazi", "Idrissi", "Fassi",
        "Berrada", "Lahlou", "Squalli", "Benjelloun", "Kettani", "Sefrioui",
        "El Amrani", "Ouazzani", "Bouzidi", "Naciri"]

# Modèles de signalements par catégorie (titre, description)
MODELES = {
    "Voirie": [
        ("Nid de poule dangereux", "Un grand trou dans la chaussée abîme les voitures"),
        ("Trottoir dégradé", "Le trottoir est fissuré et présente un risque de chute"),
        ("Affaissement de la voie", "La route s'affaisse au niveau du carrefour"),
        ("Chaussée fissurée", "De nombreuses fissures sur le bitume de l'avenue"),
    ],
    "Éclairage": [
        ("Lampadaire éteint", "L'éclairage public ne fonctionne plus depuis plusieurs jours"),
        ("Ampoule grillée", "Réverbère en panne, rue plongée dans le noir la nuit"),
        ("Luminaire défaillant", "La lampe clignote et s'éteint par intermittence"),
        ("Panne d'éclairage", "Tout le quartier est dans l'obscurité le soir"),
    ],
    "Propreté": [
        ("Dépôt sauvage d'ordures", "Tas de déchets et encombrants au coin de la rue"),
        ("Poubelle débordante", "La poubelle n'a pas été collectée, déchets partout"),
        ("Décharge improvisée", "Détritus accumulés sur un terrain vague"),
        ("Rue insalubre", "Saletés et ordures non ramassées depuis une semaine"),
    ],
    "Espaces verts": [
        ("Arbre tombé", "Une grosse branche bloque le passage dans le parc"),
        ("Pelouse à l'abandon", "Le gazon du jardin public n'est plus entretenu"),
        ("Élagage nécessaire", "Les branches d'un arbre gênent la circulation"),
        ("Arrosage en panne", "Les plantes du square se dessèchent"),
    ],
    "Sécurité": [
        ("Panneau de signalisation cassé", "Risque d'accident au carrefour sans panneau"),
        ("Feu tricolore en panne", "Le feu ne fonctionne plus, danger pour les piétons"),
        ("Barrière endommagée", "La barrière de sécurité est tombée près de l'école"),
        ("Passage glissant", "Chaussée glissante et dangereuse après la pluie"),
    ],
}

STATUTS_POIDS = [("Résolu", 0.62), ("En cours", 0.26), ("Nouveau", 0.12)]


def _statut_aleatoire():
    r = random.random()
    cumul = 0
    for statut, poids in STATUTS_POIDS:
        cumul += poids
        if r <= cumul:
            return statut
    return "Nouveau"


def seed():
    # Entraîne le modèle de classification (crée ml/model.joblib) avant tout,
    # pour que la classification des signalements utilise le vrai modèle.
    print("Entraînement du modèle de classification (Machine Learning)...")
    try:
        from ml.train import entrainer
        entrainer()
        print()
    except Exception as e:
        print(f"  (entraînement ignoré : {e} — repli sur les mots-clés)")

    engine, Session = init_engine(config.Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()

    print("Création des catégories...")
    descriptions = {
        "Voirie": "Routes, trottoirs, chaussées et infrastructures de circulation",
        "Éclairage": "Éclairage public, lampadaires et réverbères",
        "Propreté": "Collecte des déchets, propreté urbaine et salubrité",
        "Espaces verts": "Parcs, jardins, arbres et espaces végétalisés",
        "Sécurité": "Signalisation, sécurité routière et risques urbains",
    }
    for i, nom in enumerate(config.Config.CATEGORIES):
        session.add(Categorie(
            nom=nom,
            description=descriptions[nom],
            priorite_defaut=random.randint(1, 3),
        ))

    print("Création des citoyens...")
    import hashlib
    def _hash(m):
        return hashlib.sha256(m.encode("utf-8")).hexdigest()

    citoyens = []
    # Compte de démonstration facile à retenir pour la soutenance
    demo = Citoyen(
        nom="Sbai",
        prenom="Taha",
        email="citoyen@cityreport.ma",
        telephone="0612345678",
        mot_de_passe=_hash("citoyen"),
        date_inscription=date(2024, 6, 1),
    )
    citoyens.append(demo)
    session.add(demo)

    for i in range(60):
        prenom = random.choice(PRENOMS)
        nom = random.choice(NOMS)
        c = Citoyen(
            nom=nom,
            prenom=prenom,
            email=f"{prenom.lower()}.{nom.lower().replace(' ', '')}{i}@mail.ma",
            telephone=f"06{random.randint(10000000, 99999999)}",
            mot_de_passe=_hash("citoyen"),
            date_inscription=date(2024, 1, 1) + timedelta(days=random.randint(0, 500)),
        )
        citoyens.append(c)
        session.add(c)

    print("Création des agents...")
    agents = []
    for secteur in config.Config.CATEGORIES:
        for _ in range(2):
            prenom = random.choice(PRENOMS)
            nom = random.choice(NOMS)
            a = Agent(
                nom=nom,
                prenom=prenom,
                email=f"{prenom.lower()}.{nom.lower().replace(' ', '')}@ville-fes.ma",
                telephone=f"05{random.randint(10000000, 99999999)}",
                secteur=secteur,
                date_prise_fonction=date(2023, 1, 1) + timedelta(days=random.randint(0, 700)),
            )
            agents.append(a)
            session.add(a)

    session.commit()

    print("Génération des signalements...")
    signalements = []
    base_date = datetime.now() - timedelta(days=150)

    for _ in range(420):
        categorie = random.choice(config.Config.CATEGORIES)
        titre, desc = random.choice(MODELES[categorie])
        quartier = random.choice(list(QUARTIERS.keys()))
        lat0, lon0 = QUARTIERS[quartier]
        lat = lat0 + random.uniform(-0.008, 0.008)
        lon = lon0 + random.uniform(-0.008, 0.008)

        statut = _statut_aleatoire()
        agent = None
        if statut != "Nouveau":
            candidats = [a for a in agents if a.secteur == categorie]
            agent = random.choice(candidats) if candidats else None

        dt = base_date + timedelta(
            days=random.randint(0, 150),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        # La classification est faite par le module ML, pas codée en dur
        cat_predite, score = classifier(titre, desc)

        s = Signalement(
            titre=titre,
            description=desc,
            photo_url=f"https://picsum.photos/seed/cr{random.randint(1, 9999)}/400/300",
            latitude=lat,
            longitude=lon,
            quartier=quartier,
            statut=statut,
            categorie=cat_predite,
            score_confiance=score,
            citoyen_id=random.choice(citoyens).id,
            agent_id=agent.id if agent else None,
            date_creation=dt,
        )
        signalements.append(s)
        session.add(s)

    # Signalements dédiés au compte de démonstration (statuts variés)
    print("Création des signalements du compte démo...")
    demo_specs = [
        ("Éclairage", "En cours", 12, ""),
        ("Voirie", "Résolu", 40, ""),
        ("Propreté", "Nouveau", 3, ""),
        ("Espaces verts", "Résolu", 55, ""),
        ("Sécurité", "En cours", 5, "police"),
    ]
    for categorie, statut, jours, urg in demo_specs:
        titre, desc = random.choice(MODELES[categorie])
        quartier = random.choice(list(QUARTIERS.keys()))
        lat0, lon0 = QUARTIERS[quartier]
        agent = None
        if statut != "Nouveau":
            candidats = [a for a in agents if a.secteur == categorie]
            agent = random.choice(candidats) if candidats else None
        cat_predite, score = classifier(titre, desc)
        s = Signalement(
            titre=titre,
            description=desc,
            photo_url=f"https://picsum.photos/seed/demo{jours}/400/300",
            latitude=lat0 + random.uniform(-0.006, 0.006),
            longitude=lon0 + random.uniform(-0.006, 0.006),
            quartier=quartier,
            statut=statut,
            urgence=urg,
            categorie=cat_predite,
            score_confiance=score,
            citoyen_id=demo.id,
            agent_id=agent.id if agent else None,
            date_creation=datetime.now() - timedelta(days=jours),
        )
        signalements.append(s)
        session.add(s)

    # Injection de cas suspects : rafales depuis une même position par un citoyen
    print("Injection de cas suspects pour le module ML...")
    spammer = random.choice(citoyens)
    lat0, lon0 = QUARTIERS["Fès Médina"]
    burst_time = datetime.now() - timedelta(days=2)
    for k in range(6):
        titre, desc = random.choice(MODELES["Propreté"])
        cat_predite, score = classifier(titre, desc)
        s = Signalement(
            titre=titre,
            description=desc,
            photo_url=f"https://picsum.photos/seed/spam{k}/400/300",
            latitude=lat0 + 0.0001 * k,
            longitude=lon0 + 0.0001 * k,
            quartier="Fès Médina",
            statut="Nouveau",
            categorie=cat_predite,
            score_confiance=score,
            citoyen_id=spammer.id,
            agent_id=None,
            date_creation=burst_time + timedelta(minutes=8 * k),
        )
        signalements.append(s)
        session.add(s)

    session.commit()

    print("Exécution de la détection d'anomalies (Isolation Forest)...")
    resultats = detecter(signalements)
    n_anom = 0
    for sid, res in resultats.items():
        rml = ResultatML(
            signalement_id=sid,
            categorie_predite=next(
                (s.categorie for s in signalements if s.id == sid), ""
            ),
            score_confiance=next(
                (s.score_confiance for s in signalements if s.id == sid), 0.0
            ),
            is_anomalie=res["is_anomalie"],
            score_anomalie=res["score_anomalie"],
            anomalie_localisation=res["anomalie_localisation"],
            anomalie_frequence=res["anomalie_frequence"],
            raison_principale=res["raison_principale"],
        )
        session.add(rml)
        if res["is_anomalie"]:
            n_anom += 1

    session.commit()

    # Génère un historique de statut cohérent (timeline) pour chaque signalement
    print("Génération de l'historique des statuts (timeline)...")
    from models import HistoriqueStatut
    ordre = {"Nouveau": 0, "En cours": 1, "Résolu": 2}
    for s in signalements:
        cible = ordre.get(s.statut, 0)
        t0 = s.date_creation
        # Toujours : création (Nouveau)
        session.add(HistoriqueStatut(
            signalement_id=s.id, ancien_statut="", nouveau_statut="Nouveau",
            commentaire="Signalement créé par le citoyen", date_changement=t0,
        ))
        if cible >= 1:
            session.add(HistoriqueStatut(
                signalement_id=s.id, ancien_statut="Nouveau",
                nouveau_statut="En cours",
                commentaire="Pris en charge par un agent municipal",
                date_changement=t0 + timedelta(days=random.randint(1, 3)),
            ))
        if cible >= 2:
            session.add(HistoriqueStatut(
                signalement_id=s.id, ancien_statut="En cours",
                nouveau_statut="Résolu",
                commentaire="Intervention terminée, problème résolu",
                date_changement=t0 + timedelta(days=random.randint(4, 10)),
            ))
    session.commit()

    print("\n" + "=" * 50)
    print("Base CityReport créée avec succès")
    print(f"  Citoyens     : {len(citoyens)}")
    print(f"  Agents       : {len(agents)}")
    print(f"  Catégories   : {len(config.Config.CATEGORIES)}")
    print(f"  Signalements : {len(signalements)}")
    print(f"  Suspects (IA): {n_anom}")
    print("=" * 50)
    print("\nLance maintenant :  python app.py")


if __name__ == "__main__":
    seed()
