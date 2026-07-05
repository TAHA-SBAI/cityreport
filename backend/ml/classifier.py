"""
Classification automatique des signalements par catégorie.

Deux niveaux, dans cet ordre de priorité :

  1. MODÈLE ENTRAÎNÉ (principal) — un pipeline scikit-learn (TF-IDF + SVM linéaire)
     entraîné sur un jeu de données étiqueté. Voir ml/train.py pour l'entraînement
     et l'évaluation (accuracy ~98 % sur le jeu de test). Le modèle est chargé
     depuis ml/model.joblib s'il existe.

  2. MOTS-CLÉS (secours) — si le modèle n'a pas encore été entraîné (fichier absent)
     ou si scikit-learn/joblib ne sont pas disponibles, on retombe sur un
     classifieur par lexique pondéré. Cela garantit que l'application fonctionne
     toujours, même sans modèle.

Pour (ré)entraîner le modèle :  python -m ml.train
"""

import os
import re
import unicodedata

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

# ---------------------------------------------------------------------------
# 1. Chargement du modèle entraîné (une seule fois, au démarrage)
# ---------------------------------------------------------------------------
_MODEL = None
_MODEL_CLASSES = None
_MODEL_LOADED = False


def _charger_modele():
    global _MODEL, _MODEL_CLASSES, _MODEL_LOADED
    if _MODEL_LOADED:
        return
    _MODEL_LOADED = True
    try:
        import joblib
        if os.path.exists(MODEL_PATH):
            data = joblib.load(MODEL_PATH)
            _MODEL = data["pipeline"]
            _MODEL_CLASSES = data["classes"]
    except Exception:
        _MODEL = None


def _confiance_depuis_scores(pipeline, texte):
    """
    Retourne un score de confiance dans [0, 1].
    LinearSVC n'a pas de predict_proba ; on dérive une confiance de la marge
    (fonction de décision) via une softmax. Les modèles probabilistes utilisent
    predict_proba directement.
    """
    import numpy as np
    clf = pipeline.named_steps["clf"]
    if hasattr(clf, "predict_proba"):
        proba = pipeline.predict_proba([texte])[0]
        return float(np.max(proba))
    # LinearSVC : marges -> softmax
    scores = pipeline.decision_function([texte])[0]
    scores = np.atleast_1d(scores)
    e = np.exp(scores - np.max(scores))
    softmax = e / e.sum()
    return float(np.max(softmax))


# ---------------------------------------------------------------------------
# 2. Classifieur de secours par mots-clés
# ---------------------------------------------------------------------------
LEXIQUE = {
    "Voirie": {
        "route": 3, "chaussee": 3, "nid": 3, "poule": 3, "trottoir": 2,
        "bitume": 2, "asphalte": 2, "fissure": 2, "trou": 3, "voie": 2,
        "passage": 1, "bordure": 2, "affaissement": 3, "degrade": 2,
    },
    "Éclairage": {
        "lampadaire": 3, "lampe": 2, "eclairage": 3, "ampoule": 3,
        "lumiere": 2, "obscur": 2, "noir": 1, "panne": 2, "reverbere": 3,
        "luminaire": 3, "eteint": 2, "nuit": 1,
    },
    "Propreté": {
        "ordure": 3, "dechet": 3, "poubelle": 3, "depot": 2, "sauvage": 2,
        "salete": 2, "nettoyage": 2, "decharge": 3, "detritus": 3,
        "encombrant": 2, "sale": 2, "insalubre": 3,
    },
    "Espaces verts": {
        "arbre": 3, "jardin": 3, "parc": 3, "espace": 1, "vert": 2,
        "pelouse": 3, "gazon": 2, "plante": 2, "branche": 2, "haie": 2,
        "fleur": 2, "arrosage": 2, "elagage": 3,
    },
    "Sécurité": {
        "danger": 3, "accident": 3, "securite": 3, "panneau": 2, "feu": 2,
        "signalisation": 3, "vitesse": 2, "barriere": 2, "chute": 2,
        "risque": 2, "glissant": 2, "effondrement": 3,
    },
}
DEFAUT = "Voirie"


def _normaliser(texte):
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texte)


def _classifier_motscles(titre, description=""):
    texte = _normaliser(f"{titre} {description}")
    mots = texte.split()
    scores = {cat: 0 for cat in LEXIQUE}
    for cat, lexique in LEXIQUE.items():
        for mot in mots:
            if mot in lexique:
                scores[cat] += lexique[mot]
    total = sum(scores.values())
    if total == 0:
        return DEFAUT, 0.30
    categorie = max(scores, key=scores.get)
    confiance = scores[categorie] / total
    return categorie, round(min(0.98, 0.45 + confiance * 0.5), 3)


# ---------------------------------------------------------------------------
# Fonction publique : classifier()
# ---------------------------------------------------------------------------
def classifier(titre, description=""):
    """
    Retourne (categorie_predite, score_confiance).
    Utilise le modèle entraîné si disponible, sinon les mots-clés.
    """
    _charger_modele()
    texte = f"{titre} {description}".strip()

    if _MODEL is not None and texte:
        try:
            categorie = str(_MODEL.predict([texte])[0])
            confiance = _confiance_depuis_scores(_MODEL, texte)
            return categorie, round(confiance, 3)
        except Exception:
            pass  # repli sur les mots-clés

    return _classifier_motscles(titre, description)


def source_active():
    """Indique quel classifieur est utilisé (pour information/debug)."""
    _charger_modele()
    return "modele_entraine" if _MODEL is not None else "mots_cles"


if __name__ == "__main__":
    print("Classifieur actif :", source_active())
    print()
    exemples = [
        ("Nid de poule dangereux", "Un grand trou dans la chaussée avenue Hassan II"),
        ("Lampadaire éteint", "L'éclairage public ne fonctionne plus depuis 3 jours"),
        ("Dépôt sauvage d'ordures", "Tas de déchets et encombrants au coin de la rue"),
        ("Arbre tombé", "Une grosse branche bloque le passage dans le parc"),
        ("Panneau de signalisation cassé", "Risque d'accident au carrefour"),
        ("Il fait tout noir dans ma rue", ""),
        ("Les poubelles puent et débordent", ""),
    ]
    for titre, desc in exemples:
        cat, conf = classifier(titre, desc)
        print(f"{titre!r:42} -> {cat:14} (confiance {conf})")
