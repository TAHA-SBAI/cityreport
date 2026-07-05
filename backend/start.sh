#!/usr/bin/env bash
# Script de démarrage pour Render.
# Au premier lancement, on prépare la base (entraînement ML + données de démo),
# puis on lance le serveur de production gunicorn.

set -o errexit

# Prépare la base de données et le modèle ML (idempotent : recrée à chaque déploiement)
python seed.py

# Lance le serveur de production
gunicorn app:app --bind 0.0.0.0:$PORT
