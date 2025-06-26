# 📊 Analyse de Données - PME Française

## 📝 Description
Ce projet propose une solution complète d'analyse des ventes pour une PME française, permettant d'explorer la dynamique des ventes dans le temps et l'espace. Il comprend un pipeline ETL (Extract, Transform, Load) et un dashboard interactif.

## 🏗️ Architecture du Projet
Le projet est composé de deux services principaux :

1. **Service de Stockage (Port 8081)**
   - Base de données SQLite
   - Modèle en étoile pour les données de ventes
   - Tables : DIM_TEMPS, DIM_PRODUITS, DIM_MAGASINS, FAIT_VENTES

2. **Service d'Analyse (Port 8501)**
   - Dashboard Streamlit interactif
   - Pipeline ETL automatisé
   - Visualisations et analyses prédéfinies

## 🛠️ Prérequis
- Docker
- Docker Compose
- Git

## 📥 Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd data_analysis_french_sme
```

2. **Construire et lancer les services**
```bash
# Arrêter les services existants (si nécessaire)
docker-compose down

# Construire les images
docker-compose build

# Lancer les services
docker-compose up -d
```

## 🚀 Utilisation

1. **Accéder au Dashboard**
   - Ouvrir votre navigateur
   - Accéder à http://localhost:8501
   - Le dashboard propose 4 sections principales :
     - 🏠 Vue d'ensemble
     - 📋 Exploration des tables
     - 🔍 Requêtes SQL personnalisées
     - 📈 Analyses prédéfinies

2. **Fonctionnalités Principales**
   - Visualisation des KPIs de vente
   - Analyse géographique des ventes
   - Suivi des performances par produit
   - Tendances temporelles
   - Requêtes SQL personnalisées

## 🧪 Tests

Pour tester l'ensemble du projet :
```bash
# Rendre le script de test exécutable
chmod +x test_docker.sh

# Lancer les tests
./test_docker.sh
```

Le script de test vérifie :
- La construction des images Docker
- L'environnement Python et uv
- Le service de stockage SQLite
- Le pipeline ETL
- Le dashboard Streamlit

## 📊 Structure des Données

### Tables Dimensionnelles
- **DIM_TEMPS** : Dimension temporelle (date, jour, mois, année, trimestre)
- **DIM_PRODUITS** : Catalogue des produits (référence, nom, prix, stock)
- **DIM_MAGASINS** : Points de vente (ville, région, taille, effectif)

### Table de Faits
- **FAIT_VENTES** : Transactions de vente (quantité, montant, références)

## 🛑 Arrêt des Services

Pour arrêter l'application :
```bash
# Arrêter les services
docker-compose down

# Supprimer aussi les volumes si nécessaire
docker-compose down -v
```

## 📚 Technologies Utilisées
- **Python 3.12** : Langage de programmation principal
- **Streamlit** : Framework pour le dashboard
- **SQLite** : Base de données
- **Pandas** : Manipulation des données
- **Docker & Docker Compose** : Conteneurisation
- **uv** : Gestionnaire de packages Python

## 🔍 Monitoring

Pour suivre les logs en temps réel :
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f sales-analysis-dashboard
docker-compose logs -f sales-data-storage
```
