import sqlite3

def create_database_and_tables():
    """Création de la base de données et des tables vides selon le schéma MCD"""
    
    # Connexion à la base de données SQLite
    conn = sqlite3.connect('/data/sales_analysis.db')
    cursor = conn.cursor()
    
    print("🔧 Création de la base de données et des tables...")
    
    # 1. Création de la table DIM_TEMPS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DIM_TEMPS (
            ID_TEMPS INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE_COMPLETE DATE NOT NULL,
            JOUR_SEMAINE VARCHAR(20),
            MOIS VARCHAR(20),
            ANNEE INTEGER,
            TRIMESTRE INTEGER
        )
    ''')
    
    # 2. Création de la table DIM_PRODUITS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DIM_PRODUITS (
            ID_PRODUIT INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_REFERENCE_PRODUIT VARCHAR(20) UNIQUE NOT NULL,
            NOM_PRODUIT VARCHAR(100),
            PRIX_UNITAIRE DECIMAL(10,2),
            STOCK_DISPONIBLE INTEGER
        )
    ''')
    
    # 3. Création de la table DIM_MAGASINS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DIM_MAGASINS (
            ID_MAGASIN INTEGER PRIMARY KEY,
            VILLE VARCHAR(50),
            NOMBRE_SALARIES INTEGER,
            REGION VARCHAR(50),
            TAILLE_MAGASIN VARCHAR(20)
        )
    ''')
    
    # 4. Création de la table FAIT_VENTES (table de faits)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FAIT_VENTES (
            ID_VENTE INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_TEMPS INTEGER,
            ID_REFERENCE_PRODUIT VARCHAR(20) NOT NULL,
            ID_MAGASIN INTEGER,
            QUANTITE_VENDUE INTEGER,
            MONTANT_VENTE DECIMAL(10,2),
            FOREIGN KEY (ID_TEMPS) REFERENCES DIM_TEMPS(ID_TEMPS),
            FOREIGN KEY (ID_REFERENCE_PRODUIT) REFERENCES DIM_PRODUITS(ID_REFERENCE_PRODUIT),
            FOREIGN KEY (ID_MAGASIN) REFERENCES DIM_MAGASINS(ID_MAGASIN)
        )
    ''')
    
    # Validation de la création
    print("✅ Tables créées avec succès!")
    
    # Affichage des tables créées
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📋 Tables créées:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Affichage de la structure de chaque table
    for table in tables:
        table_name = table[0]
        print(f"\n🔍 Structure de {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Base de données créée avec succès!")
    print("📍 Fichier: /data/sales_analysis.db")

if __name__ == "__main__":
    create_database_and_tables()
