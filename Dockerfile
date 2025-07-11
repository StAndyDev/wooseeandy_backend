# Image Python officielle légère
FROM python:3.11-slim

# Empêche Python d'écrire des fichiers .pyc + affiche les logs direct
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installe les dépendances système utiles (notamment pour psycopg2 et uvicorn)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Crée le dossier de l'app
WORKDIR /app

# Copie les fichiers dans le conteneur
COPY . /app/

# Installe les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Rend le script de démarrage exécutable
RUN chmod +x start.sh

# Lance le script de démarrage
CMD ["./start.sh"]