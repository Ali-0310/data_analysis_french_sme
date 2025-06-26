import streamlit as st
import pandas as pd
import sqlite3
import os

def connect_to_database():
    """Connexion à la base de données SQLite"""
    db_path = './data/sales_analysis.db'
    
    if not os.path.exists(db_path):
        st.error(f"❌ Base de données non trouvée: {db_path}")
        st.info("💡 Assurez-vous d'avoir exécuté le pipeline ETL d'abord")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        st.error(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def get_table_info(conn):
    """Récupérer les informations sur les tables"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    table_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        table_info[table_name] = [col[1] for col in columns]
    
    return table_info

def execute_query(conn, query):
    """Exécuter une requête SQL et retourner les résultats"""
    try:
        df = pd.read_sql_query(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)

def show_overview(conn):
    """Afficher la vue d'ensemble de la base de données"""
    st.header("🏠 Vue d'ensemble de la base de données")
    
    # Informations sur les tables
    table_info = get_table_info(conn)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Tables disponibles")
        for table_name, columns in table_info.items():
            with st.expander(f"📋 {table_name} ({len(columns)} colonnes)"):
                st.write("**Colonnes:**")
                for col in columns:
                    st.write(f"- {col}")
    
    with col2:
        st.subheader("📊 Statistiques")
        cursor = conn.cursor()
        for table_name in table_info.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            st.metric(f"Enregistrements {table_name}", count)

def show_tables(conn):
    """Afficher le contenu des tables"""
    st.header("📋 Exploration des tables")
    
    table_info = get_table_info(conn)
    selected_table = st.selectbox("Choisir une table:", list(table_info.keys()))
    
    if selected_table:
        st.subheader(f"📊 Contenu de la table: {selected_table}")
        
        # Afficher les premières lignes
        df = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 100", conn)
        st.dataframe(df, use_container_width=True)
        
        # Statistiques de la table
        st.subheader("📊 Statistiques de la table")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre de lignes", len(df))
        
        with col2:
            st.metric("Nombre de colonnes", len(df.columns))
        
        with col3:
            numeric_cols = df.select_dtypes(include=['number']).columns
            st.metric("Colonnes numériques", len(numeric_cols))

def show_sql_queries(conn):
    """Interface pour exécuter des requêtes SQL personnalisées"""
    st.header("🔍 Requêtes SQL personnalisées")
    
    # Requêtes d'exemple
    example_queries = {
        "Sélection simple": "SELECT * FROM DIM_PRODUITS LIMIT 5",
        "Chiffre d'affaire total": """
        SELECT
        SUM(MONTANT_VENTE) AS MONTANT_VENTE_TOTAL
        FROM FAIT_VENTES
        """,
        "Ventes par produits": """
        SELECT 
            NOM_PRODUIT,
            SUM(MONTANT_VENTE) AS MONTANT_VENTE
        FROM FAIT_VENTES 
        INNER JOIN DIM_PRODUITS 
        USING(ID_REFERENCE_PRODUIT)
        GROUP BY NOM_PRODUIT
        """,
        "Ventes par region": """
        SELECT 
            dm.REGION,
            COUNT(*) as nombre_ventes,
            SUM(fv.MONTANT_VENTE) as ca_total,
            AVG(fv.MONTANT_VENTE) as panier_moyen
        FROM FAIT_VENTES fv
        JOIN DIM_MAGASINS dm ON fv.ID_MAGASIN = dm.ID_MAGASIN
        GROUP BY dm.REGION
        ORDER BY ca_total DESC
        """
    }
    
    # Sélection d'une requête d'exemple
    selected_example = st.selectbox("Choisir une requête d'exemple:", list(example_queries.keys()))
    
    # Zone de texte pour la requête SQL
    query = st.text_area(
        "Votre requête SQL:",
        value=example_queries[selected_example],
        height=200,
        help="Écrivez votre requête SQL ici. Utilisez les tables: DIM_TEMPS, DIM_PRODUITS, DIM_MAGASINS, FAIT_VENTES"
    )
    
    # Bouton d'exécution
    if st.button("🚀 Exécuter la requête", type="primary"):
        if query.strip():
            with st.spinner("Exécution de la requête..."):
                df, error = execute_query(conn, query)
                
                if error:
                    st.error(f"❌ Erreur SQL: {error}")
                else:
                    if df is not None and len(df) > 0:
                        st.success(f"✅ Requête exécutée avec succès! ({len(df)} lignes)")
                        
                        # Affichage des résultats
                        st.subheader("📊 Résultats")
                        st.dataframe(df, use_container_width=True)
                        
                        # Statistiques des résultats
                        st.subheader("📈 Statistiques des résultats")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Nombre de lignes", len(df))
                        
                        with col2:
                            st.metric("Nombre de colonnes", len(df.columns))
                        
                        with col3:
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            if len(numeric_cols) > 0:
                                st.metric("Colonnes numériques", len(numeric_cols))
                    else:
                        st.warning("⚠️ Aucun résultat retourné")
        else:
            st.warning("⚠️ Veuillez saisir une requête SQL")

def show_predefined_analyses(conn):
    """Afficher des analyses prédéfinies"""
    st.header("📈 Analyses prédéfinies")
    
    analysis_type = st.selectbox(
        "Choisir une analyse:",
        [
            "💰 CA par ville",
            "📦 Top produits",
            "📅 Évolution temporelle",
            "🏪 Performance des magasins",
            "📊 Vue d'ensemble des ventes"
        ]
    )
    
    if analysis_type == "💰 CA par ville":
        show_ca_by_city(conn)
    elif analysis_type == "📦 Top produits":
        show_top_products(conn)
    elif analysis_type == "📅 Évolution temporelle":
        show_temporal_evolution(conn)
    elif analysis_type == "🏪 Performance des magasins":
        show_store_performance(conn)
    elif analysis_type == "📊 Vue d'ensemble des ventes":
        show_sales_overview(conn)

def show_ca_by_city(conn):
    """Afficher le CA par ville"""
    st.subheader("💰 Chiffre d'affaires par ville")
    
    query = """
    SELECT 
        dm.VILLE,
        dm.REGION,
        COUNT(*) as nombre_ventes,
        SUM(fv.MONTANT_VENTE) as ca_total,
        AVG(fv.MONTANT_VENTE) as panier_moyen,
        SUM(fv.QUANTITE_VENDUE) as quantite_totale
    FROM FAIT_VENTES fv
    JOIN DIM_MAGASINS dm ON fv.ID_MAGASIN = dm.ID_MAGASIN
    GROUP BY dm.VILLE, dm.REGION
    ORDER BY ca_total DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.bar_chart(df.set_index('VILLE')['ca_total'])

def show_top_products(conn):
    """Afficher les top produits"""
    st.subheader("📦 Top produits par CA")
    
    query = """
    SELECT 
        dp.NOM_PRODUIT,
        dp.PRIX_UNITAIRE,
        SUM(fv.QUANTITE_VENDUE) as quantite_totale,
        SUM(fv.MONTANT_VENTE) as ca_total,
        COUNT(*) as nombre_ventes
    FROM FAIT_VENTES fv
    JOIN DIM_PRODUITS dp ON fv.ID_REFERENCE_PRODUIT = dp.ID_REFERENCE_PRODUIT
    GROUP BY dp.NOM_PRODUIT, dp.PRIX_UNITAIRE
    ORDER BY ca_total DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.bar_chart(df.set_index('NOM_PRODUIT')['ca_total'])

def show_temporal_evolution(conn):
    """Afficher l'évolution temporelle"""
    st.subheader("📅 Évolution des ventes dans le temps")
    
    query = """
    SELECT 
        dt.DATE_COMPLETE,
        dt.MOIS,
        dt.ANNEE,
        SUM(fv.MONTANT_VENTE) as ca_jour,
        SUM(fv.QUANTITE_VENDUE) as quantite_jour,
        COUNT(*) as nombre_ventes
    FROM FAIT_VENTES fv
    JOIN DIM_TEMPS dt ON fv.ID_TEMPS = dt.ID_TEMPS
    GROUP BY dt.DATE_COMPLETE, dt.MOIS, dt.ANNEE
    ORDER BY dt.DATE_COMPLETE
    """
    
    df = pd.read_sql_query(query, conn)
    df['DATE_COMPLETE'] = pd.to_datetime(df['DATE_COMPLETE'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.line_chart(df.set_index('DATE_COMPLETE')['ca_jour'])

def show_store_performance(conn):
    """Afficher la performance des magasins"""
    st.subheader("🏪 Performance des magasins")
    
    query = """
    SELECT 
        dm.VILLE,
        dm.NOMBRE_SALARIES,
        dm.TAILLE_MAGASIN,
        COUNT(*) as nombre_ventes,
        SUM(fv.MONTANT_VENTE) as ca_total,
        AVG(fv.MONTANT_VENTE) as panier_moyen,
        SUM(fv.QUANTITE_VENDUE) as quantite_totale
    FROM FAIT_VENTES fv
    JOIN DIM_MAGASINS dm ON fv.ID_MAGASIN = dm.ID_MAGASIN
    GROUP BY dm.VILLE, dm.NOMBRE_SALARIES, dm.TAILLE_MAGASIN
    ORDER BY ca_total DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    st.dataframe(df, use_container_width=True)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(df.set_index('VILLE')['ca_total'])
    
    with col2:
        st.bar_chart(df.set_index('VILLE')['panier_moyen'])

def show_sales_overview(conn):
    """Afficher la vue d'ensemble des ventes"""
    st.subheader("📊 Vue d'ensemble des ventes")
    
    # KPIs principaux
    kpi_query = """
    SELECT 
        COUNT(*) as total_ventes,
        SUM(MONTANT_VENTE) as ca_total,
        AVG(MONTANT_VENTE) as panier_moyen,
        SUM(QUANTITE_VENDUE) as quantite_totale
    FROM FAIT_VENTES
    """
    
    kpi_df = pd.read_sql_query(kpi_query, conn)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total ventes", f"{kpi_df['total_ventes'].iloc[0]:,}")
    
    with col2:
        st.metric("CA total", f"{kpi_df['ca_total'].iloc[0]:,.2f} €")
    
    with col3:
        st.metric("Panier moyen", f"{kpi_df['panier_moyen'].iloc[0]:.2f} €")
    
    with col4:
        st.metric("Quantité totale", f"{kpi_df['quantite_totale'].iloc[0]:,}")
    
    # Répartition par dimension
    st.subheader("📈 Répartition par dimension")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Par ville
        city_query = """
        SELECT dm.VILLE, SUM(fv.MONTANT_VENTE) as ca
        FROM FAIT_VENTES fv
        JOIN DIM_MAGASINS dm ON fv.ID_MAGASIN = dm.ID_MAGASIN
        GROUP BY dm.VILLE
        ORDER BY ca DESC
        """
        city_df = pd.read_sql_query(city_query, conn)
        st.write("**CA par ville:**")
        st.dataframe(city_df)
    
    with col2:
        # Par produit
        product_query = """
        SELECT dp.NOM_PRODUIT, SUM(fv.MONTANT_VENTE) as ca
        FROM FAIT_VENTES fv
        JOIN DIM_PRODUITS dp ON fv.ID_REFERENCE_PRODUIT = dp.ID_REFERENCE_PRODUIT
        GROUP BY dp.NOM_PRODUIT
        ORDER BY ca DESC
        """
        product_df = pd.read_sql_query(product_query, conn)
        st.write("**CA par produit:**")
        st.dataframe(product_df)

def main():
    st.set_page_config(
        page_title="Analyse des Ventes - PME Française",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Dashboard d'Analyse des Ventes - PME Française")
    st.markdown("---")
    
    # Connexion à la base de données
    conn = connect_to_database()
    if conn is None:
        st.stop()
    
    # Sidebar pour la navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choisir une section:",
        ["🏠 Vue d'ensemble", "📋 Tables", "🔍 Requêtes SQL", "📈 Analyses prédéfinies"]
    )
    
    if page == "🏠 Vue d'ensemble":
        show_overview(conn)
    elif page == "📋 Tables":
        show_tables(conn)
    elif page == "🔍 Requêtes SQL":
        show_sql_queries(conn)
    elif page == "📈 Analyses prédéfinies":
        show_predefined_analyses(conn)
    
    conn.close()

if __name__ == "__main__":
    main() 