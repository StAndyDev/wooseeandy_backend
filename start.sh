#!/bin/bash

# Attendre que la DB soit prête (optionnel)
# echo "Waiting for database..."
# sleep 5

# Migrer la base de données
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Lancer le serveur ASGI
uvicorn wooseeandy_backend.asgi:application --host 0.0.0.0 --port $PORT