"""
Jeu de données étiqueté pour l'entraînement du classifieur de signalements.

Le dataset est construit en deux parties :
  1. Des exemples "manuels" rédigés à la main (phrases réalistes variées)
  2. Une augmentation par combinaison de gabarits (sujet + problème + lieu)
     propres à chaque catégorie, pour obtenir un volume suffisant et varié.

Cette approche (data augmentation par templates) est courante quand on dispose
de peu de données réelles étiquetées. Elle donne au modèle assez d'exemples pour
généraliser. En production, ce dataset serait remplacé par des signalements
réels étiquetés par les agents municipaux.
"""

import random

random.seed(42)

# -- Gabarits par catégorie : (sujets, problèmes, lieux) --
GABARITS = {
    "Voirie": {
        "sujets": ["La route", "La chaussée", "Le trottoir", "Le bitume",
                   "Le revêtement", "La voie", "L'asphalte", "Le passage piéton",
                   "La bordure", "Le caniveau"],
        "problemes": ["est pleine de nids-de-poule", "est fissurée",
                      "s'est affaissée", "est complètement dégradée",
                      "présente un trou dangereux", "est défoncée",
                      "s'effrite", "est impraticable", "est trouée",
                      "a un revêtement abîmé", "est pleine de crevasses"],
        "lieux": ["avenue Hassan II", "près de l'école", "au carrefour",
                  "dans le quartier", "sur le boulevard", "devant le marché",
                  "au rond-point", "dans la rue principale", "près de la mosquée"],
    },
    "Éclairage": {
        "sujets": ["Le lampadaire", "L'éclairage public", "Le réverbère",
                   "Le luminaire", "L'ampoule", "La lampe de rue",
                   "Le poteau d'éclairage", "L'éclairage"],
        "problemes": ["est éteint depuis plusieurs jours", "ne fonctionne plus",
                      "clignote sans arrêt", "est grillé", "est en panne",
                      "grésille la nuit", "reste éteint le soir",
                      "est cassé", "ne s'allume plus", "fait des étincelles"],
        "lieux": ["dans la ruelle", "sur le boulevard", "près de l'arrêt de bus",
                  "devant chez moi", "dans le parc", "au passage piéton",
                  "dans le nouveau lotissement", "sur la place", "près du pont"],
    },
    "Propreté": {
        "sujets": ["La poubelle", "Le conteneur à ordures", "Un dépôt d'ordures",
                   "Un tas de déchets", "Les encombrants", "La benne",
                   "Des sacs poubelles", "Les détritus", "Une décharge sauvage"],
        "problemes": ["déborde depuis des jours", "n'a pas été ramassé",
                      "s'accumule sur le trottoir", "dégage de mauvaises odeurs",
                      "est éventré", "attire les rats", "n'a pas été vidé",
                      "bloque le passage", "pollue le quartier",
                      "reste abandonné"],
        "lieux": ["au coin de la rue", "devant l'immeuble", "près de l'école",
                  "sur un terrain vague", "dans l'impasse", "près du marché",
                  "dans le parc", "au point de collecte", "sur le trottoir"],
    },
    "Espaces verts": {
        "sujets": ["Un arbre", "Une grosse branche", "La pelouse", "Le gazon",
                   "L'espace vert", "La haie", "Le massif de fleurs",
                   "L'arrosage automatique", "L'arbuste", "Le jardin public"],
        "problemes": ["est tombé et bloque le passage", "menace de tomber",
                      "n'est plus entretenu", "est desséché", "est à l'abandon",
                      "doit être élagué", "est malade", "est piétiné",
                      "n'est plus arrosé", "envahit le trottoir"],
        "lieux": ["dans le parc", "au jardin public", "sur la place",
                  "au square", "près de l'aire de jeux", "le long de l'avenue",
                  "dans le jardin municipal", "près des bancs", "à l'entrée du quartier"],
    },
    "Sécurité": {
        "sujets": ["Le panneau stop", "Le feu tricolore", "La barrière de sécurité",
                   "La signalisation", "La glissière", "Le panneau de danger",
                   "La rambarde", "Le passage à niveau", "Le dos d'âne",
                   "La plaque d'égout"],
        "problemes": ["est arraché au carrefour", "est en panne",
                      "est cassé près de l'école", "manque au croisement",
                      "est tordu au bord de la route", "est renversé",
                      "est descellé et dangereux", "n'est pas signalé",
                      "provoque des accidents", "présente un risque de chute"],
        "lieux": ["au carrefour dangereux", "près de l'école", "sur la route",
                  "au croisement", "au bord du ravin", "sur le pont",
                  "en zone scolaire", "à l'intersection", "sur le chantier"],
    },
}

# Exemples rédigés à la main (phrases naturelles, tournures variées)
MANUELS = [
    ("Nid de poule dangereux qui abîme les pneus des voitures", "Voirie"),
    ("Plaque d'égout descellée au milieu de la chaussée", "Voirie"),
    ("Le marquage au sol est complètement effacé", "Voirie"),
    ("Route inondée à cause d'un mauvais écoulement des eaux", "Voirie"),
    ("Pavés descellés sur toute la place centrale", "Voirie"),
    ("Trottoir trop abîmé pour passer avec une poussette", "Voirie"),
    ("Ralentisseur trop haut qui casse les suspensions", "Voirie"),

    ("Toute la rue est plongée dans le noir la nuit", "Éclairage"),
    ("Plusieurs lampadaires hors service sur l'avenue", "Éclairage"),
    ("Câble d'éclairage qui pend dangereusement du poteau", "Éclairage"),
    ("Le projecteur du stade municipal est en panne", "Éclairage"),
    ("Zone sombre et dangereuse près de l'arrêt de bus", "Éclairage"),
    ("Coupures de lumière à répétition dans le quartier", "Éclairage"),

    ("Ordures ménagères jamais collectées dans cette rue", "Propreté"),
    ("Gravats de chantier déversés illégalement", "Propreté"),
    ("Insalubrité et odeurs nauséabondes dans la ruelle", "Propreté"),
    ("Carcasse de meuble abandonnée sur le trottoir", "Propreté"),
    ("Restes alimentaires qui attirent les nuisibles", "Propreté"),
    ("Déchets verts non ramassés depuis des semaines", "Propreté"),

    ("Racines d'arbre qui soulèvent et cassent le trottoir", "Espaces verts"),
    ("Palmier penché dangereusement au-dessus de la place", "Espaces verts"),
    ("Système d'irrigation cassé au jardin municipal", "Espaces verts"),
    ("Arbre foudroyé à sécuriser en urgence", "Espaces verts"),
    ("Aire de jeux envahie par les mauvaises herbes", "Espaces verts"),
    ("Grande branche arrachée par le vent sur la pelouse", "Espaces verts"),

    ("Feux de signalisation éteints à un grand carrefour", "Sécurité"),
    ("Câbles électriques tombés à terre après la tempête", "Sécurité"),
    ("Mur qui menace de s'effondrer sur la rue", "Sécurité"),
    ("Bouche d'incendie qui fuit et inonde la route", "Sécurité"),
    ("Zone scolaire sans aucun passage piéton sécurisé", "Sécurité"),
    ("Éboulement de pierres sur la route de montagne", "Sécurité"),

    # Tournures naturelles supplémentaires (langage courant, pluriels)
    ("Les lampadaires sont tous éteints dans ma rue", "Éclairage"),
    ("Il fait tout noir le soir, plus aucune lumière", "Éclairage"),
    ("Y'a plus d'éclairage depuis une semaine", "Éclairage"),
    ("Les poubelles puent et débordent partout", "Propreté"),
    ("C'est sale, personne ne ramasse les ordures", "Propreté"),
    ("Il y a des déchets partout sur le trottoir", "Propreté"),
    ("La route est pleine de trous, c'est dangereux", "Voirie"),
    ("Ma rue est défoncée, impossible de rouler", "Voirie"),
    ("Les arbres ne sont plus taillés dans le parc", "Espaces verts"),
    ("Le gazon est tout sec, personne ne l'arrose", "Espaces verts"),
    ("Le feu rouge ne marche plus, c'est dangereux", "Sécurité"),
    ("Il manque un panneau au carrefour, ça cause des accidents", "Sécurité"),
    ("Plusieurs ampoules de rue sont grillées", "Éclairage"),
    ("Grosse fuite d'eau qui inonde toute la chaussée", "Voirie"),
]


def _augmenter(n_par_categorie=120):
    """Génère des exemples variés par combinaison de gabarits."""
    exemples = []
    for cat, g in GABARITS.items():
        combos = set()
        essais = 0
        while len(combos) < n_par_categorie and essais < n_par_categorie * 20:
            essais += 1
            sujet = random.choice(g["sujets"])
            probleme = random.choice(g["problemes"])
            lieu = random.choice(g["lieux"])
            phrase = f"{sujet} {probleme} {lieu}"
            if phrase not in combos:
                combos.add(phrase)
                exemples.append((phrase, cat))
    return exemples


def get_dataset():
    """Retourne (textes, labels) : exemples manuels + augmentés."""
    data = list(MANUELS) + _augmenter()
    random.shuffle(data)
    textes = [t for t, _ in data]
    labels = [c for _, c in data]
    return textes, labels


if __name__ == "__main__":
    from collections import Counter
    textes, labels = get_dataset()
    print(f"Total : {len(textes)} exemples")
    for cat, n in Counter(labels).most_common():
        print(f"  {cat:16} : {n} exemples")
    print("\nExemples générés :")
    for t, c in list(zip(textes, labels))[:6]:
        print(f"  [{c:14}] {t}")
