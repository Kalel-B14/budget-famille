import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os # Pour vérifier l'existence du fichier
# Note: SQLAlchemy est importé seulement si vous l'utilisez pour une base de données.
# Comme il n'apparaît pas dans les imports principaux, je le laisse ici commenté.
# import sqlalchemy 

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Budget Famille 2025", layout="wide")

# --- FONCTION DE CHARGEMENT ET NETTOYAGE DES DONNÉES ---
@st.cache_data
def load_data(filepath):
    """
    Charge les données du CSV, en gérant l'en-tête et en nettoyant les colonnes.
    Le fichier 'Données_2025.csv' a l'en-tête à la ligne 1 (index 1), et
    nécessite un nettoyage pour garantir que les colonnes monétaires sont numériques.
    """
    if not os.path.exists(filepath):
        st.error(f"Fichier de données non trouvé : {filepath}")
        return pd.DataFrame()

    try:
        # Lire le fichier, l'en-tête (header) est à l'index 1 (la 2ème ligne)
        df = pd.read_csv(filepath, header=1)

        # Retirer les lignes vides et la ligne 'TOTAL'
        df = df.dropna(subset=['Catégories']).copy()
        df = df[df['Catégories'] != 'TOTAL\xa0:']
        
        # S'assurer que la colonne 'Montant par catégorie' est numérique.
        # Cela devrait corriger l'erreur ArrowTypeError.
        df['Montant par catégorie'] = pd.to_numeric(
            df['Montant par catégorie'], errors='coerce'
        ).fillna(0)
        
        # Renommer pour la simplicité
        df = df.rename(columns={'Montant par catégorie': 'Montant'})

        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement ou du nettoyage des données : {e}")
        return pd.DataFrame()


# --- CHEMIN D'ACCÈS DU FICHIER DE DONNÉES ---
# Utilisez le nom de fichier correct de votre dépôt
DATA_FILE = "Budgets_Famille.xlsx - Données_2025.csv"

# Chargement des données
df_budget = load_data(DATA_FILE)

# --- AFFICHAGE DE L'APPLICATION ---
st.title("💰 Aperçu du Budget Familial")

if not df_budget.empty:
    st.header("Répartition par Catégorie")
    
    # Création du graphique en secteurs (Pie Chart)
    fig_pie = px.pie(
        df_budget, 
        values='Montant', 
        names='Catégories', 
        title='Pourcentage des Dépenses par Catégorie',
        color_discrete_sequence=px.colors.sequential.Agsunset,
        # Utiliser 'width' au lieu de 'use_container_width' (comme suggéré dans les logs)
        # Bien que Streamlit le gère généralement dans st.plotly_chart
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Données Détaillées")
    # Utiliser st.dataframe pour une meilleure affichage interactif
    st.dataframe(df_budget[['Catégories', 'Montant', 'Fréquence', 'Total']], hide_index=True)
else:
    st.info("Veuillez vous assurer que le fichier de données est présent et correctement formaté.")
