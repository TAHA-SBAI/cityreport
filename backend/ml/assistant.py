"""
Assistant conversationnel de CityReport.

Approche : détection d'intention par mots-clés pondérés sur une base de
connaissances propre à l'application. Chaque intention a des déclencheurs
(mots-clés) et une réponse rédigée. La question de l'utilisateur est normalisée
puis comparée ; l'intention au meilleur score l'emporte.

Cette approche est locale (aucune clé API, fonctionne hors-ligne) et parfaitement
adaptée à un assistant de domaine fermé comme celui-ci. Elle se remplace
facilement par un LLM en branchant une API dans repondre().
"""

import re
import unicodedata

# Base de connaissances : intention -> (mots-clés déclencheurs, réponse)
CONNAISSANCES = [
    {
        "intent": "salutation",
        "cles": ["bonjour", "salut", "bonsoir", "coucou", "hello", "hi", "salam"],
        "reponse": "Bonjour 👋 Je suis l'assistant de CityReport. Je peux vous "
                   "expliquer comment signaler un problème, suivre vos demandes "
                   "ou contacter les services d'urgence. Que puis-je faire pour vous ?",
    },
    {
        "intent": "comment_signaler",
        "cles": ["signaler", "signalement", "declarer", "creer",
                 "envoyer", "deposer"],
        "reponse": "Pour signaler un problème : cliquez sur « Nouveau signalement », "
                   "donnez un titre et une description, prenez ou choisissez une "
                   "photo, puis placez le point exact sur la carte. Notre IA classe "
                   "automatiquement votre demande dans la bonne catégorie. C'est tout !",
    },
    {
        "intent": "categories",
        "cles": ["categorie", "categories", "type", "types",
                 "problemes", "voirie", "eclairage", "proprete"],
        "reponse": "Vous pouvez signaler 5 types de problèmes : 🛣️ Voirie (routes, "
                   "trottoirs), 💡 Éclairage public, 🗑️ Propreté (déchets), 🌳 Espaces "
                   "verts (parcs, arbres) et 🚸 Sécurité (signalisation, dangers).",
    },
    {
        "intent": "photo",
        "cles": ["photo", "image", "camera", "appareil", "prendre", "joindre"],
        "reponse": "Oui, vous pouvez ajouter une photo à votre signalement. Sur "
                   "téléphone, le bouton photo ouvre directement l'appareil photo. "
                   "Une image aide beaucoup les agents à comprendre le problème.",
    },
    {
        "intent": "urgence",
        "cles": ["urgence", "urgent", "police", "danger", "secours", "19", "15",
                 "accident", "grave", "emergency", "aide"],
        "reponse": "En cas de danger immédiat, utilisez le bouton d'urgence lors du "
                   "signalement : il vous permet d'appeler directement la police "
                   "(19) ou les secours / SAMU (15). Pour un problème non urgent, "
                   "un signalement normal suffit.",
    },
    {
        "intent": "suivi",
        "cles": ["suivi", "suivre", "statut", "etat", "avancement", "traite",
                 "resolu", "delai", "attente"],
        "reponse": "Après un signalement, suivez son avancement dans « Mes "
                   "signalements ». Chaque demande passe par 3 étapes : Nouveau → "
                   "En cours → Résolu, avec la date de chaque changement. Vous voyez "
                   "ainsi exactement où en est votre demande.",
    },
    {
        "intent": "compte",
        "cles": ["compte", "inscription", "inscrire", "connecter", "connexion",
                 "login", "mot", "passe", "email"],
        "reponse": "Pour utiliser CityReport, créez un compte gratuit avec votre "
                   "email et un mot de passe. Vous pourrez ensuite déposer des "
                   "signalements et suivre leur traitement depuis votre espace.",
    },
    {
        "intent": "ia",
        "cles": ["ia", "intelligence", "artificielle", "automatique", "classe",
                 "classification", "detecte", "algorithme", "machine", "learning"],
        "reponse": "CityReport utilise l'intelligence artificielle de deux façons : "
                   "elle classe automatiquement chaque signalement dans la bonne "
                   "catégorie, et elle détecte les signalements suspects ou en "
                   "double (par exemple plusieurs alertes identiques au même endroit).",
    },
    {
        "intent": "confidentialite",
        "cles": ["donnees", "prive", "confidentiel", "securite", "personnel",
                 "protege", "anonyme"],
        "reponse": "Vos données personnelles ne servent qu'au traitement de vos "
                   "signalements par les services municipaux. Elles ne sont ni "
                   "vendues ni partagées à des tiers.",
    },
    {
        "intent": "remerciement",
        "cles": ["merci", "thanks", "parfait", "super", "genial", "cool"],
        "reponse": "Avec plaisir ! 😊 N'hésitez pas si vous avez d'autres questions "
                   "sur CityReport.",
    },
]

# Réponse par défaut si aucune intention ne ressort
DEFAUT = ("Je suis l'assistant de CityReport. Je peux vous aider sur : comment "
          "faire un signalement, les types de problèmes, l'ajout de photos, les "
          "urgences (19/15), le suivi de vos demandes ou la création d'un compte. "
          "Posez-moi une question sur l'un de ces sujets !")

# Suggestions affichées au démarrage du chat
SUGGESTIONS = [
    "Comment signaler un problème ?",
    "Quels types de problèmes puis-je signaler ?",
    "Comment contacter les urgences ?",
    "Comment suivre mon signalement ?",
]


def _normaliser(texte: str) -> str:
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texte)


def repondre(question: str) -> dict:
    """Retourne {reponse, intent, score} pour une question donnée."""
    texte = _normaliser(question or "")
    mots = set(texte.split())

    meilleur = None
    meilleur_score = 0
    for entree in CONNAISSANCES:
        score = sum(1 for cle in entree["cles"] if cle in mots)
        if score > meilleur_score:
            meilleur_score = score
            meilleur = entree

    if meilleur and meilleur_score > 0:
        return {"reponse": meilleur["reponse"], "intent": meilleur["intent"],
                "score": meilleur_score}
    return {"reponse": DEFAUT, "intent": "defaut", "score": 0}


if __name__ == "__main__":
    tests = [
        "Bonjour",
        "Comment je fais pour signaler un nid de poule ?",
        "Je peux mettre une photo ?",
        "C'est urgent, il y a un accident !",
        "Où en est mon signalement ?",
        "Comment marche l'IA ?",
    ]
    for t in tests:
        r = repondre(t)
        print(f"Q: {t}\nA: {r['reponse']}\n   (intent={r['intent']}, score={r['score']})\n")
