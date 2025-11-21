import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
import os
import random
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Budget Familial (Importation & Base de Données)", layout="wide")

# --- INITIALISATION DE FIREBASE (SIMULÉE) ET CHARGEMENT DES DONNÉES D'IMPORTATION ---
if 'db_initialised' not in st.session_state:
    st.session_state.db_initialised = False
    st.session_state.data = []  # Stockage des dépenses pour la simulation
    st.session_state.db = "Simulated Local DB"
    st.session_state.user_id = "demo-user-" + str(random.randint(1000, 9999)) # ID utilisateur simulé
    st.session_state.import_done = False # Drapeau pour l'importation

    # Tenter de charger les données initiales du JSON
    try:
        if os.path.exists("initial_budget_data.json"):
            with open("initial_budget_data.json", 'r', encoding='utf-8') as f:
                initial_data = json.load(f)
                st.session_state.initial_import_data = initial_data
                st.session_state.db_initialised = True
        else:
            st.session_state.initial_import_data = []
            st.warning("Fichier 'initial_budget_data.json' non trouvé. Veuillez exécuter 'data_prep.py' d'abord.")
            st.session_state.db_initialised = True # Initialisation de la session réussie
            
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier JSON d'importation : {e}")
        st.session_state.db_initialised = False


# --- FONCTIONS DE GESTION DES DONNÉES PERSISTANTES (SIMULÉES) ---

def fetch_expenses():
    """Charge toutes les dépenses depuis la base de données (ou la session)."""
    # Dans un vrai environnement Firestore, ceci serait un onSnapshot
    return st.session_state.data

def add_expense(category, amount, frequency, description, timestamp=None):
    """Ajoute une nouvelle dépense à la base de données (ou la session)."""
    new_expense = {
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Timestamp': timestamp if timestamp else time.time()
    }
    
    # Logique d'écriture : ici, nous écrivons dans la variable de session (simulation)
    st.session_state.data.append(new_expense)
    
    if not timestamp: # N'afficher le toast que pour les ajouts manuels
        st.toast("Dépense ajoutée avec succès !", icon='✅')

def handle_import():
    """Importe les données du fichier JSON dans la base de données de session."""
    if st.session_state.initial_import_data and not st.session_state.import_done:
        st.info(f"Importation de {len(st.session_state.initial_import_data)} transactions de l'historique...")
        
        # Effacer les données existantes avant l'importation
        st.session_state.data = [] 
        
        for expense in st.session_state.initial_import_data:
            # Injecter les données en utilisant le timestamp d'origine
            add_expense(
                expense['Catégories'], 
                expense['Montant'], 
                expense['Fréquence'], 
                expense['Description'], 
                timestamp=expense['Timestamp']
            )
        
        st.session_state.import_done = True
        st.toast("Importation de l'historique terminée !", icon='🎉')
        st.rerun() # Recharger l'interface pour afficher les nouvelles données

# --- INTERFACE UTILISATEUR ---

st.title("💰 Suivi du Budget Familial (Démo Firestore)")

# 0. BOUTON D'IMPORTATION DE L'HISTORIQUE
if st.session_state.initial_import_data and not st.session_state.import_done:
    st.warning("Historique de budget trouvé ! Cliquez ci-dessous pour l'importer dans la base de données.")
    if st.button("Importer les données historiques (2025/2026)"):
        handle_import()
        
if not st.session_state.db_initialised:
    st.error("L'application n'a pas pu s'initialiser correctement. Veuillez vérifier les fichiers.")
    st.stop()


# 1. FORMULAIRE D'AJOUT DE DÉPENSE
with st.expander("➕ Ajouter une nouvelle dépense manuelle"):
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_category = st.selectbox(
                "Catégorie",
                options=['Maison', 'Alimentation', 'Transport', 'Épargne', 'Loisirs', 'Santé', 'Abonnements', 'Autre']
            )
            expense_amount = st.number_input("Montant (€)", min_value=0.01, step=5.0)
        
        with col2:
            expense_frequency = st.selectbox(
                "Fréquence",
                options=['Mensuel', 'Annuel', 'Trimestriel', 'Unique', 'Hebdomadaire']
            )
            expense_description = st.text_input("Description (facultatif)")
        
        submitted = st.form_submit_button("Enregistrer la dépense")
        
        if submitted:
            if expense_amount > 0:
                add_expense(expense_category, expense_amount, expense_frequency, expense_description)
            else:
                st.error("Le montant doit être supérieur à zéro.")

# 2. AFFICHAGE ET ANALYSE DES DONNÉES
expenses_list = fetch_expenses()

if expenses_list:
    df_expenses = pd.DataFrame(expenses_list)
    
    # Agrégation par catégorie (pour le graphique)
    df_agg = df_expenses.groupby('Catégories')['Montant'].sum().reset_index()
    df_agg.rename(columns={'Montant': 'Total Dépensé (€)'}, inplace=True)
    
    # Total Global
    total_spent = df_expenses['Montant'].sum()

    st.header("Analyse des Dépenses Totales")
    st.metric(label="Total des Dépenses Enregistrées (Historique + Manuelles)", value=f"{total_spent:,.2f} €")

    st.subheader("Répartition des Dépenses par Catégorie")
    
    # Création du graphique en secteurs (Pie Chart)
    fig_pie = px.pie(
        df_agg, 
        values='Total Dépensé (€)', 
        names='Catégories', 
        title='Pourcentage des Dépenses Totales',
        color_discrete_sequence=px.colors.sequential.Agsunset,
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Détail des Transactions")
    # Tri par date, les entrées importées auront un Timestamp plus ancien (elles seront en bas)
    df_display = df_expenses.sort_values(by='Timestamp', ascending=False)
    
    # Ajout d'une colonne de date formatée pour une meilleure lisibilité
    df_display['Date Ajout'] = df_display['Timestamp'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M'))

    st.dataframe(
        df_display[['Date Ajout', 'Catégories', 'Montant', 'Fréquence', 'Description']],
        column_config={
            "Montant": st.column_config.NumberColumn("Montant (€)", format="%.2f"),
        },
        hide_index=True
    )
    
else:
    st.info("Aucune dépense enregistrée. Importez l'historique ou ajoutez manuellement une dépense !")

st.markdown("""
<style>
/* Corrige un petit problème de padding en bas de page */
.stApp { padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)
