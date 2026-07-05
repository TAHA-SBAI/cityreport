-- Schéma de référence CityReport (PostgreSQL)
-- SQLAlchemy crée ces tables automatiquement ; ce fichier sert de documentation
-- et de point de départ pour un déploiement PostgreSQL manuel.

CREATE TABLE IF NOT EXISTS citoyens (
    id               SERIAL PRIMARY KEY,
    nom              VARCHAR(80)  NOT NULL,
    prenom           VARCHAR(80)  NOT NULL,
    email            VARCHAR(160) UNIQUE NOT NULL,
    telephone        VARCHAR(40)  DEFAULT '',
    mot_de_passe     VARCHAR(200) DEFAULT '',
    date_inscription DATE         DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS agents (
    id                  SERIAL PRIMARY KEY,
    nom                 VARCHAR(80)  NOT NULL,
    prenom              VARCHAR(80)  NOT NULL,
    email               VARCHAR(160) UNIQUE NOT NULL,
    telephone           VARCHAR(40)  DEFAULT '',
    secteur             VARCHAR(60)  NOT NULL,
    date_prise_fonction DATE         DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS categories (
    id              SERIAL PRIMARY KEY,
    nom             VARCHAR(60) UNIQUE NOT NULL,
    description     TEXT       DEFAULT '',
    priorite_defaut INTEGER    DEFAULT 2
);

CREATE TABLE IF NOT EXISTS signalements (
    id              SERIAL PRIMARY KEY,
    titre           VARCHAR(160) NOT NULL,
    description     TEXT         DEFAULT '',
    photo_url       VARCHAR(300) DEFAULT '',
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    quartier        VARCHAR(80)  DEFAULT '',
    date_creation   TIMESTAMP    DEFAULT NOW(),
    statut          VARCHAR(20)  DEFAULT 'Nouveau',
    urgence         VARCHAR(20)  DEFAULT '',
    categorie       VARCHAR(60)  DEFAULT '',
    score_confiance DOUBLE PRECISION DEFAULT 0,
    citoyen_id      INTEGER REFERENCES citoyens(id),
    agent_id        INTEGER REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS resultats_ml (
    id                    SERIAL PRIMARY KEY,
    signalement_id        INTEGER UNIQUE REFERENCES signalements(id) ON DELETE CASCADE,
    categorie_predite     VARCHAR(60)      DEFAULT '',
    score_confiance       DOUBLE PRECISION DEFAULT 0,
    is_anomalie           BOOLEAN          DEFAULT FALSE,
    score_anomalie        DOUBLE PRECISION DEFAULT 0,
    anomalie_localisation BOOLEAN          DEFAULT FALSE,
    anomalie_frequence    BOOLEAN          DEFAULT FALSE,
    raison_principale     VARCHAR(120)     DEFAULT ''
);

-- Historique des changements de statut (timeline citoyen)
CREATE TABLE IF NOT EXISTS historique_statuts (
    id              SERIAL PRIMARY KEY,
    signalement_id  INTEGER REFERENCES signalements(id) ON DELETE CASCADE,
    ancien_statut   VARCHAR(20)  DEFAULT '',
    nouveau_statut  VARCHAR(20)  NOT NULL,
    commentaire     VARCHAR(240) DEFAULT '',
    date_changement TIMESTAMP    DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signalements_categorie ON signalements(categorie);
CREATE INDEX IF NOT EXISTS idx_signalements_statut    ON signalements(statut);
CREATE INDEX IF NOT EXISTS idx_signalements_quartier  ON signalements(quartier);
CREATE INDEX IF NOT EXISTS idx_historique_signalement ON historique_statuts(signalement_id);
