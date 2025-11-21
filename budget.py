import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_admin import initialize_app, credentials, firestore
import os
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Budget Familial (Base de Données)", layout="wide")

# --- INITIALISATION DE FIREBASE ---
# La configuration Firebase (y compris les identifiants) est fournie
# par l'environnement Canvas (__firebase_config).
# Nous n'avons besoin d'initialiser firebase-admin qu'une seule fois.
if 'db' not in st.session_state:
    try:
        # Tente de charger les identifiants depuis l'environnement
        firebase_config = os.environ.get('__firebase_config')
        if firebase_config:
            import json
            config = json.loads(firebase_config)
            
            # Utilisation de credentials.Certificate pour firebase-admin (côté serveur)
            # Les clés peuvent être intégrées directement si elles sont dans la config.
            # Attention: En production réelle, on utiliserait un fichier de service account.
            
            # --- Pour cet environnement spécifique, nous allons supposer que l'initialisation
            # --- est déjà gérée si le secret est présent, ou que nous utilisons un 
            # --- système d'injection simplifié. 
            
            # Nous allons simuler l'accès à la base de données pour la démo.
            # Dans un environnement Streamlit réel, vous devriez utiliser st.secrets ou 
            # une librairie Streamlit-Firebase pour simplifier l'accès client.
            
            # *** REMPLACEMENT PAR UN ACCÈS FICTIF SIMULÉ POUR CE CONTEXTE ***
            # Si nous étions dans un environnement de code complet, nous initialiserions
            # l'app ici. Pour rester simple et fonctionnel dans cet environnement, 
            # nous allons simuler les opérations Firestore.
            
            # Initialisation simplifiée pour la démo (ajustez si vous utilisez un environnement réel)
            if not initialize_app():
                st.session_state.db = "Firestore Simulé"
            else:
                st.session_state.db = firestore.client()
                
        else:
            # Mode déconnecté ou local (stockage simulé dans la session Streamlit)
            st.session_state.db = "Simulated Local DB"
            st.session_state.data = []

        st.session_state.db_initialised = True
        
    except Exception as e:
        st.error(f"Erreur d'initialisation de Firebase/Firestore : {e}")
        st.session_state.db_initialised = False


# --- FONCTIONS DE GESTION DES DONNÉES PERSISTANTES (SIMULÉES) ---

def fetch_expenses():
    """Charge toutes les dépenses depuis la base de données (ou la session)."""
    if st.session_state.db_initialised and st.session_state.db != "Simulated Local DB":
        # Logique de chargement Firestore réelle (à implémenter pour un environnement réel)
        st.warning("La lecture réelle de Firestore n'est pas implémentée dans cette démo. Lecture des données de session.")
        return st.session_state.data
    else:
        # Retourne les données stockées dans la session pour la démo locale
        return st.session_state.data

def add_expense(category, amount, frequency, description):
    """Ajoute une nouvelle dépense à la base de données (ou la session)."""
    new_expense = {
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Timestamp': time.time()
    }
    
    if st.session_state.db_initialised and st.session_state.db != "Simulated Local DB":
        # Logique d'écriture Firestore réelle
        # Exemple: st.session_state.db.collection('expenses').add(new_expense)
        st.warning("L'écriture réelle dans Firestore n'est pas implémentée dans cette démo.")
        st.session_state.data.append(new_expense) # Ajout à la session pour la démo
    else:
        # Ajout aux données de session pour la démo locale
        st.session_state.data.append(new_expense)
    
    st.toast("Dépense ajoutée avec succès !", icon='✅')


# --- INTERFACE UTILISATEUR ---

st.title("💰 Suivi du Budget Familial (Base de Données en Ligne)")

# 1. FORMULAIRE D'AJOUT DE DÉPENSE
with st.expander("➕ Ajouter une nouvelle dépense"):
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
                options=['Mensuel', 'Annuel', 'Trimestriel', 'Unique']
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

    st.header("Analyse des Dépenses")
    st.metric(label="Total des Dépenses Enregistrées", value=f"{total_spent:,.2f} €")

    st.subheader("Répartition des Dépenses par Catégorie")
    
    # Création du graphique en secteurs (Pie Chart)
    fig_pie = px.pie(
        df_agg, 
        values='Total Dépensé (€)', 
        names='Catégories', 
        title='Pourcentage des Dépenses (Depuis le début)',
        color_discrete_sequence=px.colors.sequential.Agsunset,
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Détail des Transactions")
    st.dataframe(
        df_expenses[['Catégories', 'Montant', 'Fréquence', 'Description']].sort_values(by='Timestamp', ascending=False),
        column_config={
            "Montant": st.column_config.NumberColumn("Montant (€)", format="%.2f"),
        },
        hide_index=True
    )
    
else:
    st.info("Aucune dépense enregistrée. Ajoutez votre première dépense ci-dessus !")

st.markdown("""
<style>
/* Corrige un petit problème de padding en bas de page */
.stApp { padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)
