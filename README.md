# CityReport — Plateforme de signalement citoyen intelligent

Application full-stack reproduisant le projet décrit dans le rapport PFA :
signalement citoyen (photo, texte, géolocalisation), classification automatique
par catégorie, détection des signalements suspects/doublons par Machine Learning
(Isolation Forest), carte interactive et tableaux de bord.

## Architecture

```
cityreport/
├── backend/              API REST Flask + SQLAlchemy
│   ├── app.py            Point d'entrée + factory Flask
│   ├── models.py         Modèles ORM (Citoyen, Agent, Catégorie, Signalement, ResultatML)
│   ├── routes/           Blueprints API (auth, signalements, agents, citoyens, stats, ml, export)
│   ├── ml/               Module Machine Learning
│   │   ├── classifier.py   Classification automatique par mots-clés + règles
│   │   └── anomaly.py      Détection d'anomalies (Isolation Forest, scikit-learn)
│   ├── seed.py           Génération de données fictives réalistes
│   ├── config.py         Configuration (SQLite par défaut, bascule PostgreSQL possible)
│   └── requirements.txt
└── frontend/             Interface React (Vite)
    ├── src/
    │   ├── App.jsx
    │   ├── pages/        Dashboard, Carte, Historique, Agents, ML, Paramètres
    │   ├── components/   Sidebar, KpiCard, charts, etc.
    │   ├── api.js        Client API
    │   └── theme.css     Design system (couleurs civic/doré)
    └── package.json
```

## Stack technique

| Couche      | Technologies                                          |
|-------------|-------------------------------------------------------|
| Frontend    | React 18, Vite, React Router, Recharts, React-Leaflet |
| Backend     | Flask, Flask-CORS, SQLAlchemy                          |
| Base        | SQLite (par défaut) — bascule PostgreSQL en 1 ligne   |
| ML          | scikit-learn (Isolation Forest), pandas, numpy        |

## Démarrage rapide

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # crée et remplit la base SQLite avec des données fictives
python app.py                   # démarre l'API sur http://localhost:5000
```

> **Mise à jour depuis une version précédente ?** Si tu avais déjà lancé le projet
> avant l'ajout de l'espace citoyen, relance simplement `python seed.py` : il
> recrée la base avec les nouvelles tables (comptes citoyens + historique de statut).

### 2. Frontend (dans un autre terminal)

```bash
cd frontend
npm install
npm run dev                     # démarre l'interface sur http://localhost:5173
```

Ouvre http://localhost:5173 dans ton navigateur.

### Deux espaces

L'application a **deux faces** :

**Espace citoyen** (page d'accueil, publique et moderne) — le citoyen crée un compte,
signale un problème en plaçant un point sur la carte, **prend une photo depuis son
téléphone**, choisit si c'est une **urgence** (bouton d'appel direct police 19 / secours 15),
voit la catégorie prédite par l'IA en direct, et suit l'avancement de ses signalements
sur une timeline (Nouveau → En cours → Résolu). Un **assistant IA conversationnel**
(bouton 💬 en bas à gauche) répond aux questions courantes sur l'application.

**Espace municipalité** (console d'administration) — accessible via le bouton
« 🔒 Accès municipalité » en bas à droite de l'accueil : dashboards, carte
globale, détection IA, gestion des agents.

### Connexions de démonstration

Espace citoyen :
- **Email** : `citoyen@cityreport.ma`
- **Mot de passe** : `citoyen`

Espace municipalité (admin) :
- **Email** : `admin@cityreport.ma`
- **Mot de passe** : `admin`

## Basculer vers PostgreSQL

Dans `backend/config.py`, remplace l'URL SQLite par :

```python
SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost:5432/cityreport"
```

Installe le pilote (`pip install psycopg2-binary`), puis relance `python seed.py`.

## Module Machine Learning

Le module ML est appelé automatiquement à la création d'un signalement :

1. **Classification supervisée** (`ml/classifier.py`) — un modèle **entraîné**
   (TF-IDF + SVM linéaire, scikit-learn) prédit la catégorie du signalement à
   partir de son texte. Le modèle est comparé à d'autres (Naive Bayes, Régression
   Logistique) puis évalué sur un jeu de test : **~98 % d'exactitude**. Si le
   modèle n'est pas encore entraîné, un classifieur par mots-clés prend le relais.
2. **Détection d'anomalies** (`ml/anomaly.py`) — un modèle Isolation Forest
   entraîné sur l'historique repère les signalements suspects : rafales depuis
   une même position, coordonnées ou horaires incohérents, doublons probables.
3. **Assistant conversationnel** (`ml/assistant.py`) — répond aux questions des
   citoyens sur l'application (détection d'intention par mots-clés).

### Entraînement et évaluation du modèle de classification

L'entraînement est lancé automatiquement par `seed.py`. Pour le relancer seul et
régénérer le rapport d'évaluation :

```bash
python -m ml.train
```

Cela produit :
- `ml/model.joblib` — le pipeline entraîné (vectoriseur + modèle), utilisé par l'app
- `ml/rapport_modele.txt` — les métriques d'évaluation (accuracy, précision,
  rappel, F1 par catégorie, matrice de confusion, comparaison des modèles).
  **C'est le document à présenter en soutenance.**

Le jeu de données étiqueté se trouve dans `ml/dataset.py` (~630 exemples,
équilibrés sur les 5 catégories). Pour améliorer le modèle, il suffit d'enrichir
ce dataset puis de relancer l'entraînement.

Pour ré-entraîner la détection d'anomalies sur toute la base :

```bash
python -m ml.anomaly --retrain
```

## Notes

- Les données sont **fictives** mais structurées comme des données réelles.
  Remplacer le `seed.py` par un import de signalements réels suffit : le reste
  du pipeline (base → ML → API → affichage) fonctionne sans modification.
- Les photos sont simulées par des URLs ; le champ existe pour brancher un
  vrai stockage de fichiers.
