import sqlite3
import os

def test_database_connection():
    """Test de connexion à la base de données SQLite"""
    
    db_path = '/data/sales_analysis.db'
    
    # Vérification de l'existence du fichier
    if os.path.exists(db_path):
        print(f"✅ Base de données trouvée: {db_path}")
    else:
        print(f"❌ Base de données non trouvée: {db_path}")
        return
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Connexion à la base de données réussie!")
        
        # Vérification des tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables trouvées ({len(tables)}):")
        for table in tables:
            print(f"- {table[0]}")
        
        # Vérification du nombre d'enregistrements par table
        print("\n📊 Nombre d'enregistrements par table:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"- {table_name}: {count} enregistrements")
        
        # Test d'une requête simple
        print("\n🔍 Test de requête:")
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"Version SQLite: {version}")
        
        conn.close()
        print("\n✅ Test de connexion terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_database_connection() 