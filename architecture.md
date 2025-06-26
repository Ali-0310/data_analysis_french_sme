# Architecture du Système d'Analyse de Données

## Schéma d'Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE DU SYSTÈME                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│                                 │    │                                 │
│    SERVICE D'ANALYSE            │    │    SERVICE DE STOCKAGE          │
│    ET DASHBOARD                 │    │                                 │
│                                 │    │  Nom: DataStorageService        │
│  Nom: SalesAnalysisDashboard    │    │                                 │
│                                 │    │  Objectif:                      │
│  Objectif:                      │    │  - Stocker les données CSV      │
│  - Interface utilisateur web    │    │  - Gérer l'accès aux données    │
│  - Exécuter les scripts         │    │  - Fournir les données          │
│    d'analyse de ventes          │    │    aux scripts d'analyse        │
│  - Visualisation interactive    │    │  - Assurer la persistance       │
│  - Analyse en temps réel        │    │    des résultats d'analyse      │
│  - Mise en ligne directe        │    │                                 │
│                                 │    │  Port exposé: 8081              │
│  Port exposé: 8501              │    │                                 │
│  URL: streamlit.app             │    │                                 │
└─────────────────────────────────┘    └─────────────────────────────────┘
                │                                    │
                │                                    │
                │  Communication HTTP/JSON           │
                │  Sens: Bidirectionnel              │
                │                                    │
                ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTERFACE DE COMMUNICATION                   │
│                                                                 │
│  Entrées:                                                       │
│  - Requêtes de données (GET /data/{type})                       │
│  - Commandes d'analyse (POST /analyze)                          │
│  - Sauvegarde de résultats (POST /save)                         │
│  - Interactions utilisateur (Streamlit)                         │
│                                                                 │
│  Sorties:                                                       │
│  - Données CSV (ventes, produits, magasins)                     │
│  - Résultats d'analyse (JSON)                                   │
│  - Dashboard web interactif                                     │
│  - Rapports et visualisations                                   │
│                                                                 │
│  Ports utilisés:                                                │
│  - 8501: Service d'analyse et dashboard                         │
│  - 8081: Service de stockage                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Détails des Services

### 1. Service d'Analyse et Dashboard (SalesAnalysisDashboard)
- **Port**: 8501
- **Objectif principal**: Service unifié combinant analyse de données et interface utilisateur
- **Fonctionnalités**:
  - Interface web interactive avec Streamlit
  - Chargement et traitement des données CSV
  - Exécution des algorithmes d'analyse temporelle
  - Exécution des algorithmes d'analyse spatiale
  - Visualisations en temps réel
  - Filtres et sélecteurs dynamiques
  - Export de rapports
  - Déploiement direct sur Streamlit Cloud

### 2. Service de Stockage (DataStorageService)
- **Port**: 8081
- **Objectif principal**: Gérer la persistance et l'accès aux données
- **Fonctionnalités**:
  - Stockage des fichiers CSV (ventes, produits, magasins)
  - Cache des données fréquemment utilisées
  - Sauvegarde des résultats d'analyse
  - API REST pour l'accès aux données

## Communication entre Services

### Sens de Communication
1. **SalesAnalysisDashboard → DataStorageService**:
   - Requêtes de lecture des données CSV
   - Sauvegarde des résultats d'analyse

2. **DataStorageService → SalesAnalysisDashboard**:
   - Réponses avec les données demandées
   - Confirmations de sauvegarde

### Protocole de Communication
- **Protocole**: HTTP/JSON pour les APIs, accès direct aux fichiers pour Streamlit
- **Format des échanges**: REST API + accès direct aux données
- **Sécurité**: Authentification basique (pour la production)
- **Déploiement**: Streamlit Cloud pour le service unifié 