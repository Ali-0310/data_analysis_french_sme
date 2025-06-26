import sqlite3
import pandas as pd
import os
from etl_script import extract_data, transform_data, load_data_conditionally

def test_extraction():
    """Test de l'étape d'extraction"""
    print("🧪 Test 1: Extraction des données")
    print("=" * 50)
    
    df_ventes, df_produits, df_magasins = extract_data()
    
    if df_ventes is not None and df_produits is not None and df_magasins is not None:
        print("✅ Extraction réussie!")
        print(f"📊 Ventes: {len(df_ventes)} lignes")
        print(f"📦 Produits: {len(df_produits)} lignes")
        print(f"🏪 Magasins: {len(df_magasins)} lignes")
        
        # Aperçu des données
        print("\n📋 Aperçu des données ventes:")
        print(df_ventes.head())
        
        return True
    else:
        print("❌ Échec de l'extraction")
        return False

def test_transformation():
    """Test de l'étape de transformation"""
    print("\n🧪 Test 2: Transformation des données")
    print("=" * 50)
    
    # Extraction d'abord
    df_ventes, df_produits, df_magasins = extract_data()
    if df_ventes is None:
        print("❌ Impossible de tester la transformation sans extraction")
        return False
    
    # Transformation
    df_dates, df_produits_transformed, df_magasins_transformed, df_faits = transform_data(
        df_ventes, df_produits, df_magasins
    )
    
    print("✅ Transformation réussie!")
    print(f"📅 Dates uniques: {len(df_dates)}")
    print(f"📦 Produits transformés: {len(df_produits_transformed)}")
    print(f"🏪 Magasins transformés: {len(df_magasins_transformed)}")
    print(f"💰 Faits de ventes: {len(df_faits)}")
    
    # Vérification des colonnes
    print("\n🔍 Vérification des colonnes:")
    print(f"DIM_TEMPS: {list(df_dates.columns)}")
    print(f"DIM_PRODUITS: {list(df_produits_transformed.columns)}")
    print(f"DIM_MAGASINS: {list(df_magasins_transformed.columns)}")
    print(f"FAIT_VENTES: {list(df_faits.columns)}")
    
    return True

def test_database_connection():
    """Test de connexion à la base de données"""
    print("\n🧪 Test 3: Connexion à la base de données")
    print("=" * 50)
    
    db_path = './data/sales_analysis.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérification des tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("✅ Connexion réussie!")
        print(f"📋 Tables trouvées: {[table[0] for table in tables]}")
        
        # Vérification du nombre d'enregistrements
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} enregistrements")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_full_etl():
    """Test complet du pipeline ETL"""
    print("\n🧪 Test 4: Pipeline ETL complet")
    print("=" * 50)
    
    try:
        # Étape 1: Extraction
        df_ventes, df_produits, df_magasins = extract_data()
        if df_ventes is None:
            return False
        
        # Étape 2: Transformation
        df_dates, df_produits_transformed, df_magasins_transformed, df_faits = transform_data(
            df_ventes, df_produits, df_magasins
        )
        
        # Étape 3: Ingestion
        load_data_conditionally(df_dates, df_produits_transformed, df_magasins_transformed, df_faits)
        
        print("✅ Pipeline ETL complet réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le pipeline ETL: {e}")
        return False

def test_data_quality():
    """Test de qualité des données"""
    print("\n🧪 Test 5: Qualité des données")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('./data/sales_analysis.db')
        
        # Test d'intégrité référentielle
        print("🔍 Test d'intégrité référentielle...")
        
        # Vérification des clés étrangères
        query = """
        SELECT COUNT(*) as total_ventes,
               COUNT(CASE WHEN fv.ID_TEMPS IS NULL THEN 1 END) as ventes_sans_temps,
               COUNT(CASE WHEN fv.ID_PRODUIT IS NULL THEN 1 END) as ventes_sans_produit,
               COUNT(CASE WHEN fv.ID_MAGASIN IS NULL THEN 1 END) as ventes_sans_magasin
        FROM FAIT_VENTES fv
        """
        
        result = pd.read_sql(query, conn)
        print(f"Total ventes: {result['total_ventes'].iloc[0]}")
        print(f"Ventes sans temps: {result['ventes_sans_temps'].iloc[0]}")
        print(f"Ventes sans produit: {result['ventes_sans_produit'].iloc[0]}")
        print(f"Ventes sans magasin: {result['ventes_sans_magasin'].iloc[0]}")
        
        # Test de requête d'analyse
        print("\n📊 Test de requête d'analyse...")
        query_analysis = """
        SELECT 
            dt.MOIS,
            dm.VILLE,
            dp.NOM_PRODUIT,
            SUM(fv.QUANTITE_VENDUE) as TOTAL_QUANTITE,
            SUM(fv.MONTANT_VENTE) as CA_TOTAL
        FROM FAIT_VENTES fv
        JOIN DIM_TEMPS dt ON fv.ID_TEMPS = dt.ID_TEMPS
        JOIN DIM_MAGASINS dm ON fv.ID_MAGASIN = dm.ID_MAGASIN
        JOIN DIM_PRODUITS dp ON fv.ID_PRODUIT = dp.ID_PRODUIT
        GROUP BY dt.MOIS, dm.VILLE, dp.NOM_PRODUIT
        ORDER BY CA_TOTAL DESC
        LIMIT 5
        """
        
        result_analysis = pd.read_sql(query_analysis, conn)
        print("Top 5 des ventes par mois/ville/produit:")
        print(result_analysis)
        
        conn.close()
        print("✅ Tests de qualité terminés!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les tests de qualité: {e}")
        return False

def run_all_tests():
    """Exécution de tous les tests"""
    print("🚀 Démarrage des tests ETL")
    print("=" * 60)
    
    tests = [
        ("Extraction", test_extraction),
        ("Transformation", test_transformation),
        ("Connexion DB", test_database_connection),
        ("Pipeline complet", test_full_etl),
        ("Qualité données", test_data_quality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans le test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des tests
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{test_name:20} : {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n🎯 Score: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 Tous les tests sont passés avec succès!")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_option = sys.argv[1].lower()
        
        if test_option == "extract":
            test_extraction()
        elif test_option == "transform":
            test_transformation()
        elif test_option == "db":
            test_database_connection()
        elif test_option == "etl":
            test_full_etl()
        elif test_option == "quality":
            test_data_quality()
        else:
            print("Options disponibles:")
            print("  python test_etl.py extract   - Test extraction")
            print("  python test_etl.py transform - Test transformation")
            print("  python test_etl.py db        - Test connexion DB")
            print("  python test_etl.py etl       - Test pipeline complet")
            print("  python test_etl.py quality   - Test qualité données")
            print("  python test_etl.py           - Tous les tests")
    else:
        run_all_tests() 