# Utilisation de l'image Python officielle 3.11
FROM python:3.12-slim-bookworm

# Définition du répertoire de travail
WORKDIR /sme_data_analysis_app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    gcc 

# Ajout du dernier installeur uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ajout de uv au PATH
ENV PATH="/root/.local/bin/:$PATH"

# Création d'un environnement virtuel avec uv
RUN uv venv /sme_data_analysis_app/.venv

# Activation de l'environnement virtuel
ENV PATH="/sme_data_analysis_app/.venv/bin:$PATH"

# Copie des fichiers de dépendances
COPY pyproject.toml .

# Installation des dépendances avec uv sync (méthode officielle)
RUN uv sync

# Copie du code source
COPY . .

# Rendre les scripts exécutables
RUN chmod +x test_etl.py main.py

# Exposition du port pour Streamlit
EXPOSE 8501

# Configuration de Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Commande par défaut pour lancer l'application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.serverAddress=localhost"] 