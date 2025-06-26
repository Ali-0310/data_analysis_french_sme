import pandas as pd
import sqlite3
import requests
import io
from datetime import datetime

def extract_data():
    """Étape 1: Extraction des données depuis les URLs"""
    print("📥 Étape 1: Extraction des données...")
    
    # URLs des fichiers de données
    url_ventes = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=760830694&single=true&output=csv"
    url_produits = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=0&single=true&output=csv"
    url_magasins = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=714623615&single=true&output=csv"
    
    try:
        # Extraction des données ventes
        response_ventes = requests.get(url_ventes)
        response_ventes.raise_for_status()
        df_ventes = pd.read_csv(io.StringIO(response_ventes.content.decode('utf-8')))
        print(f"✅ Données ventes extraites: {len(df_ventes)} lignes")
        
        # Extraction des données produits
        response_produits = requests.get(url_produits)
        response_produits.raise_for_status()
        df_produits = pd.read_csv(io.StringIO(response_produits.content.decode('utf-8')))
        print(f"✅ Données produits extraites: {len(df_produits)} lignes")
        
        # Extraction des données magasins
        response_magasins = requests.get(url_magasins)
        response_magasins.raise_for_status()
        df_magasins = pd.read_csv(io.StringIO(response_magasins.content.decode('utf-8')))
        print(f"✅ Données magasins extraites: {len(df_magasins)} lignes")
        
        return df_ventes, df_produits, df_magasins
        
    except requests.RequestException as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return None, None, None

def transform_data(df_ventes, df_produits, df_magasins):
    """Étape 2: Transformation des données selon le schéma MCD"""
    print("\n🔄 Étape 2: Transformation des données...")
    
    # Transformation des données temporelles (DIM_TEMPS)
    print("📅 Transformation des données temporelles...")
    df_ventes['Date'] = pd.to_datetime(df_ventes['Date'])
    
    df_dates = pd.DataFrame({
        'DATE_COMPLETE': df_ventes['Date'],
        'JOUR_SEMAINE': pd.to_datetime(df_ventes['Date']).dt.day_name(),
        'MOIS': pd.to_datetime(df_ventes['Date']).dt.month_name(),
        'ANNEE': pd.to_datetime(df_ventes['Date']).dt.year,
        'TRIMESTRE': pd.to_datetime(df_ventes['Date']).dt.quarter
    })
    
    # Transformation des données produits (DIM_PRODUITS)
    print("📦 Transformation des données produits...")
    df_produits_transformed = df_produits.rename(columns={
        'ID Référence produit': 'ID_REFERENCE_PRODUIT',
        'Nom': 'NOM_PRODUIT',
        'Prix': 'PRIX_UNITAIRE',
        'Stock': 'STOCK_DISPONIBLE'
    })
    
    # Transformation des données magasins (DIM_MAGASINS)
    print("🏪 Transformation des données magasins...")
    df_magasins_transformed = df_magasins.rename(columns={
        'ID Magasin': 'ID_MAGASIN',
        'Ville': 'VILLE',
        'Nombre de salariés': 'NOMBRE_SALARIES'
    })
    
    # Ajout des colonnes calculées pour les magasins
    region_mapping = {
        'Paris': 'Île-de-France',
        'Marseille': 'Provence-Alpes-Côte d\'Azur',
        'Lyon': 'Auvergne-Rhône-Alpes',
        'Bordeaux': 'Nouvelle-Aquitaine',
        'Lille': 'Hauts-de-France',
        'Nantes': 'Pays de la Loire',
        'Strasbourg': 'Grand Est'
    }
    
    df_magasins_transformed['REGION'] = df_magasins_transformed['VILLE'].map(region_mapping)
    df_magasins_transformed['TAILLE_MAGASIN'] = df_magasins_transformed['NOMBRE_SALARIES'].apply(
        lambda x: 'Petit' if x < 5 else 'Moyen' if x <= 10 else 'Grand'
    )
    
    # Transformation des données de ventes (FAIT_VENTES)
    print("💰 Transformation des données de ventes...")
    
    # Création du mapping date vers ID_TEMPS
    date_to_id = dict(zip(df_dates['DATE_COMPLETE'], range(1, len(df_dates) + 1)))
    
 
    
    # Création de la table de faits
    df_faits = df_ventes.copy()
    df_faits['ID_TEMPS'] = df_faits['Date'].map(date_to_id)
    df_faits['ID_MAGASIN'] = df_faits['ID Magasin']
    df_faits['QUANTITE_VENDUE'] = df_faits['Quantité']
    df_faits['ID_REFERENCE_PRODUIT'] = df_faits['ID Référence produit']
    
    # Calcul du montant de vente
    prix_produits = dict(zip(df_produits_transformed['ID_REFERENCE_PRODUIT'], df_produits_transformed['PRIX_UNITAIRE']))
    df_faits['MONTANT_VENTE'] = df_faits['ID Référence produit'].map(prix_produits) * df_faits['QUANTITE_VENDUE']
    
    # Sélection des colonnes finales pour FAIT_VENTES
    df_faits_final = df_faits[['ID_TEMPS', 'ID_REFERENCE_PRODUIT', 'ID_MAGASIN', 'QUANTITE_VENDUE', 'MONTANT_VENTE']]
    
    print("✅ Transformation terminée!")
    return df_dates, df_produits_transformed, df_magasins_transformed, df_faits_final

def load_data_conditionally(df_dates, df_produits, df_magasins, df_faits):
    """Étape 3: Ingestion conditionnelle des données"""
    print("\n💾 Étape 3: Ingestion conditionnelle des données...")
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('./data/sales_analysis.db')
        cursor = conn.cursor()
        
        # Fonction pour vérifier si des données existent déjà
        def data_exists(table_name, check_column, check_values):
            placeholders = ','.join(['?' for _ in check_values])
            query = f"SELECT COUNT(*) FROM {table_name} WHERE {check_column} IN ({placeholders})"
            cursor.execute(query, check_values)
            return cursor.fetchone()[0] > 0
        
        # Ingestion conditionnelle DIM_TEMPS
        print("📅 Ingestion DIM_TEMPS...")
        if not data_exists('DIM_TEMPS', 'DATE_COMPLETE', df_dates['DATE_COMPLETE'].dt.strftime('%Y-%m-%d').tolist()):
            df_dates.to_sql('DIM_TEMPS', conn, if_exists='append', index=False)
            print(f"✅ {len(df_dates)} nouvelles dates insérées")
        else:
            print("ℹ️ Données temporelles déjà présentes")
        
        # Ingestion conditionnelle DIM_PRODUITS
        print("📦 Ingestion DIM_PRODUITS...")
        if not data_exists('DIM_PRODUITS', 'ID_REFERENCE_PRODUIT', df_produits['ID_REFERENCE_PRODUIT'].tolist()):
            df_produits.to_sql('DIM_PRODUITS', conn, if_exists='append', index=False)
            print(f"✅ {len(df_produits)} nouveaux produits insérés")
        else:
            print("ℹ️ Données produits déjà présentes")
        
        # Ingestion conditionnelle DIM_MAGASINS
        print("🏪 Ingestion DIM_MAGASINS...")
        if not data_exists('DIM_MAGASINS', 'ID_MAGASIN', df_magasins['ID_MAGASIN'].tolist()):
            df_magasins.to_sql('DIM_MAGASINS', conn, if_exists='append', index=False)
            print(f"✅ {len(df_magasins)} nouveaux magasins insérés")
        else:
            print("ℹ️ Données magasins déjà présentes")
        
        # Ingestion conditionnelle FAIT_VENTES
        print("💰 Ingestion FAIT_VENTES...")
        # Vérification basée sur la combinaison des clés
        existing_ventes = pd.read_sql("""
            SELECT ID_TEMPS, ID_REFERENCE_PRODUIT, ID_MAGASIN, COUNT(*) as count 
            FROM FAIT_VENTES 
            GROUP BY ID_TEMPS, ID_REFERENCE_PRODUIT, ID_MAGASIN
        """, conn)
        
        if len(existing_ventes) == 0:
            df_faits.to_sql('FAIT_VENTES', conn, if_exists='append', index=False)
            print(f"✅ {len(df_faits)} nouvelles ventes insérées")
        else:
            print("ℹ️ Données de ventes déjà présentes")
        
        # Validation finale
        print("\n📊 Validation des données:")
        cursor.execute("SELECT COUNT(*) FROM DIM_TEMPS")
        print(f"- DIM_TEMPS: {cursor.fetchone()[0]} enregistrements")
        
        cursor.execute("SELECT COUNT(*) FROM DIM_PRODUITS")
        print(f"- DIM_PRODUITS: {cursor.fetchone()[0]} enregistrements")
        
        cursor.execute("SELECT COUNT(*) FROM DIM_MAGASINS")
        print(f"- DIM_MAGASINS: {cursor.fetchone()[0]} enregistrements")
        
        cursor.execute("SELECT COUNT(*) FROM FAIT_VENTES")
        print(f"- FAIT_VENTES: {cursor.fetchone()[0]} enregistrements")
        
        conn.commit()
        conn.close()
        print("\n✅ Ingestion terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ingestion: {e}")
        if 'conn' in locals():
            conn.close()

def main():
    """Pipeline ETL principal"""
    print("🚀 Démarrage du pipeline ETL...")
    
    # Étape 1: Extraction
    df_ventes, df_produits, df_magasins = extract_data()
    if df_ventes is None:
        print("❌ Échec de l'extraction. Arrêt du pipeline.")
        return
    
    # Étape 2: Transformation
    df_dates, df_produits_transformed, df_magasins_transformed, df_faits = transform_data(
        df_ventes, df_produits, df_magasins
    )
    
    # Étape 3: Ingestion conditionnelle
    load_data_conditionally(df_dates, df_produits_transformed, df_magasins_transformed, df_faits)
    
    print("\n🎉 Pipeline ETL terminé avec succès!")

if __name__ == "__main__":
    main() 