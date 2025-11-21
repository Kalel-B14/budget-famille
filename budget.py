import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
import os
import random
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Budget Familial (Importation & Base de Données)", layout="wide")

# --- INITIALISATION DE FIREBASE ---

# Vérifier si Firebase a déjà été initialisé
if not firebase_admin._apps:
    # Récupérer les secrets de Firebase depuis Streamlit Cloud
    firebase_secrets = st.secrets["firebase"]

    # Créer un dictionnaire à partir des secrets pour utiliser Firebase
    cred_dict = {
        "type": firebase_secrets["type"],
        "project_id": firebase_secrets["project_id"],
        "private_key_id": firebase_secrets["private_key_id"],
        "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),  # Le format de la clé privée est spécial
        "client_email": firebase_secrets["client_email"],
        "client_id": firebase_secrets["client_id"],
        "auth_uri": firebase_secrets["auth_uri"],
        "token_uri": firebase_secrets["token_uri"],
        "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
    }

    # Initialiser Firebase avec les secrets (en spécifiant un nom unique pour éviter l'erreur de réinitialisation)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, name="budget-famille-app")  # Ajout d'un nom unique pour l'application

# Accéder à Firestore
db = firestore.client()

# --- FONCTIONS DE GESTION DES DONNÉES FIRESTORE ---

def add_expense_to_firestore(category, amount, frequency, description, timestamp=None):
    """Ajoute une dépense à Firebase Firestore."""
    expense_ref = db.collection('expenses').document()  # Créer un document unique pour chaque dépense
    expense_ref.set({
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Timestamp': timestamp if timestamp else time.time()
    })
    st.toast("Dépense ajoutée avec succès !", icon='✅')

def fetch_expenses_from_firestore():
    """Charge les dépenses depuis Firestore."""
    expenses_ref = db.collection('expenses')  # Accéder à la collection 'expenses'
    docs = expenses_ref.stream()  # Récupérer tous les documents

    expenses = []
    for doc in docs:
        expenses.append(doc.to_dict())  # Convertir chaque document en dictionnaire Python
    return expenses

# --- INITIALISATION DE LA SESSION ET CHARGEMENT DES DONNÉES ---
if 'db_initialised' not in st.session_state:
    st.session_state.db_initialised = False
    st.session_state.data = fetch_expenses_from_firestore()  # Charger les données depuis Firestore
    st.session_state.db = "Firestore DB"
    st.session_state.user_id = "demo-user-" + str(random.randint(1000, 9999))  # ID utilisateur simulé
    st.session_state.import_done = False  # Drapeau pour l'importation

# --- INTERFACE UTILISATEUR ---
st.title("💰 Suivi du Budget Familial (Démo Firebase)")

# 0. BOUTON D'IMPORTATION DE L'HISTORIQUE
if not st.session_state.db_initialised:
    st.error("L'application n'a pas pu s'initialiser correctement. Veuillez vérifier la connexion à Firebase.")
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
                add_expense_to_firestore(expense_category, expense_amount, expense_frequency, expense_description)
            else:
                st.error("Le montant doit être supérieur à zéro.")

# 2. AFFICHAGE ET ANALYSE DES DONNÉES
expenses_list = st.session_state.data

if expenses_list:
    df_expenses = pd.DataFrame(expenses_list)
    
    # Agrégation par catégorie (pour le graphique)
    df_agg = df_expenses.groupby('Catégories')['Montant'].sum().reset_index()
    df_agg.rename(columns={'Montant': 'Total Dépensé (€)'}, inplace=True)
    
    # Total Global
    total_spent = df_expenses['Montant'].sum()

    st.header("Analyse des Dépenses Totales")
    st.metric(label="Total des Dépenses Enregistrées", value=f"{total_spent:,.2f} €")

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
    
else:
    st.info("Aucune dépense enregistrée. Ajoutez une dépense manuelle !")

st.markdown(""" 
<style> 
/* Corrige un petit problème de padding en bas de page */ 
.stApp { padding-bottom: 2rem; } 
</style> 
""", unsafe_allow_html=True)
