#!/bin/bash

echo "=== Test de l'architecture Docker pour l'analyse des ventes ==="
echo "=================================================="

echo "🔨 1. Construction de l'image d'analyse..."
docker build -t sales-analysis .

echo ""
echo "🔍 2. Vérification de l'environnement Python et uv..."
docker run --rm sales-analysis bash -c "
    echo '📍 Python path:'
    which python
    echo '📦 uv version:'
    uv --version
"

echo ""
echo "💾 3. Test du service de stockage SQLite..."
docker run --rm -v $(pwd)/data:/data alpine:latest sh -c "
    echo '📥 Installation de SQLite...'
    apk add --no-cache sqlite python3
    echo '✅ SQLite installé avec succès'
    sqlite3 --version
    echo '🔄 Service de stockage prêt'
"

echo ""
echo "🚀 4. Démarrage des services Docker..."
echo "🔄 Arrêt des services existants..."
docker-compose down
echo "📤 Suppression des volumes..."
docker-compose down -v
echo "🔄 Démarrage des nouveaux services..."
docker-compose up -d

echo ""
echo "📋 5. Vérification des conteneurs..."
docker-compose ps

echo ""
echo "🔍 6. Test du service de stockage..."
echo "Version SQLite:"
docker exec sales-data-storage sqlite --version
echo "Structure de la base de données:"
docker exec sales-data-storage sqlite ./data/sales_analysis.db ".tables"
docker exec sales-data-storage sqlite ./data/sales_analysis.db ".schema"

echo ""
echo "📊 7. Test du pipeline ETL..."
docker exec sales-analysis-dashboard python test_etl.py

echo ""
echo "🌐 8. Test de l'application Streamlit..."
echo "Vérification du processus Streamlit:"
docker exec sales-analysis-dashboard ps aux | grep streamlit
echo "Logs de l'application:"
docker-compose logs --tail=10 sales-analysis-dashboard

echo ""
echo "=== 🎯 Tests terminés ==="
echo "✅ Dashboard accessible sur: http://localhost:8501"
echo "✅ Service de stockage sur le port: 8081"
echo "✅ Base de données: /data/sales_analysis.db"
echo ""
echo "Pour accéder au dashboard:"
echo "1. Ouvrez votre navigateur"
echo "2. Accédez à http://localhost:8501"
echo "3. Vous devriez voir l'interface d'analyse des ventes"
echo ""
echo "Pour arrêter les services:"
echo "$ docker-compose down"
echo ""
echo "Pour voir les logs en temps réel:"
echo "$ docker-compose logs -f" 