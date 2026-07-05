"""
Entraînement et évaluation du classifieur de signalements CityReport.

Démarche (typique d'un projet de Machine Learning) :
  1. Chargement du jeu de données étiqueté (ml/dataset.py)
  2. Séparation entraînement / test (stratifiée, 75 % / 25 %)
  3. Vectorisation du texte par TF-IDF (avec n-grammes de mots)
  4. Comparaison de plusieurs modèles : Naive Bayes, Régression Logistique,
     SVM linéaire — chacun évalué par validation croisée
  5. Sélection du meilleur modèle, ré-entraînement sur tout le train
  6. Évaluation finale sur le jeu de test : accuracy, precision, recall, F1,
     et matrice de confusion
  7. Sauvegarde du pipeline (vectoriseur + modèle) sur disque + rapport texte

Usage :
    python -m ml.train

Produit :
    ml/model.joblib        le pipeline entraîné (utilisé par classifier.py)
    ml/rapport_modele.txt  les métriques d'évaluation (à montrer en soutenance)
"""

import os
from collections import Counter

from ml.dataset import get_dataset

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "rapport_modele.txt")


def entrainer():
    # Imports scikit-learn locaux (pour que le reste du projet marche sans sklearn)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import LinearSVC
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import (
        accuracy_score, classification_report, confusion_matrix,
    )
    import joblib
    import numpy as np

    textes, labels = get_dataset()
    classes = sorted(set(labels))

    # 1. Séparation train / test (stratifiée pour garder l'équilibre des classes)
    X_train, X_test, y_train, y_test = train_test_split(
        textes, labels, test_size=0.25, random_state=42, stratify=labels
    )

    lignes = []
    def log(s=""):
        print(s)
        lignes.append(s)

    log("=" * 60)
    log("  ENTRAÎNEMENT DU CLASSIFIEUR CityReport")
    log("=" * 60)
    log(f"Jeu de données : {len(textes)} exemples, {len(classes)} catégories")
    log(f"  Entraînement : {len(X_train)} exemples")
    log(f"  Test         : {len(X_test)} exemples")
    log("")

    # 2. Un vectoriseur TF-IDF commun (mots + bigrammes, sans accents)
    def make_pipeline(clf):
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                lowercase=True, strip_accents="unicode",
                ngram_range=(1, 2), min_df=1, sublinear_tf=True,
            )),
            ("clf", clf),
        ])

    modeles = {
        "Naive Bayes": make_pipeline(MultinomialNB()),
        "Régression Logistique": make_pipeline(
            LogisticRegression(max_iter=1000, C=10)
        ),
        "SVM linéaire": make_pipeline(LinearSVC(C=1.0)),
    }

    # 3. Comparaison par validation croisée (5 plis) sur le train
    log("Comparaison des modèles (validation croisée 5 plis) :")
    log("-" * 60)
    scores_cv = {}
    for nom, pipe in modeles.items():
        n_splits = min(5, min(Counter(y_train).values()))
        scores = cross_val_score(pipe, X_train, y_train, cv=n_splits, scoring="accuracy")
        scores_cv[nom] = scores.mean()
        log(f"  {nom:24} : {scores.mean():.3f} (± {scores.std():.3f})")
    log("")

    # 4. Sélection du meilleur modèle
    meilleur_nom = max(scores_cv, key=scores_cv.get)
    log(f"➜ Meilleur modèle retenu : {meilleur_nom}")
    log("")

    meilleur = modeles[meilleur_nom]
    meilleur.fit(X_train, y_train)

    # 5. Évaluation finale sur le jeu de test
    y_pred = meilleur.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    log("=" * 60)
    log("  ÉVALUATION FINALE SUR LE JEU DE TEST")
    log("=" * 60)
    log(f"Exactitude (accuracy) : {acc:.1%}")
    log("")
    log("Rapport de classification (précision / rappel / F1) :")
    log("-" * 60)
    rapport = classification_report(
        y_test, y_pred, labels=classes, zero_division=0
    )
    log(rapport)

    # 6. Matrice de confusion
    log("Matrice de confusion (lignes = réel, colonnes = prédit) :")
    log("-" * 60)
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    entete = "".join(f"{c[:8]:>10}" for c in classes)
    log(f"{'':16}{entete}")
    for i, c in enumerate(classes):
        ligne = "".join(f"{cm[i][j]:>10}" for j in range(len(classes)))
        log(f"{c:16}{ligne}")
    log("")

    # 7. Ré-entraînement sur TOUT le dataset (train+test) pour le modèle final
    #    déployé, puis sauvegarde.
    modele_final = make_pipeline(
        {
            "Naive Bayes": MultinomialNB(),
            "Régression Logistique": LogisticRegression(max_iter=1000, C=10),
            "SVM linéaire": LinearSVC(C=1.0),
        }[meilleur_nom]
    )
    modele_final.fit(textes, labels)
    joblib.dump({"pipeline": modele_final, "classes": classes,
                 "modele": meilleur_nom, "accuracy_test": acc}, MODEL_PATH)

    log(f"Modèle final ré-entraîné sur les {len(textes)} exemples et sauvegardé :")
    log(f"  {MODEL_PATH}")
    log("")
    log("Ce modèle est maintenant utilisé automatiquement par l'application.")

    # Écriture du rapport
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))
    print(f"\nRapport d'évaluation écrit dans : {REPORT_PATH}")

    return acc


if __name__ == "__main__":
    entrainer()
