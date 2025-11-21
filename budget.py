import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import random
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Budget Familial Complet", layout="wide")

# --- INITIALISATION DE FIREBASE ---
if not firebase_admin._apps:
    firebase_secrets = st.secrets["firebase"]
    cred_dict = {
        "type": firebase_secrets["type"],
        "project_id": firebase_secrets["project_id"],
        "private_key_id": firebase_secrets["private_key_id"],
        "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),
        "client_email": firebase_secrets["client_email"],
        "client_id": firebase_secrets["client_id"],
        "auth_uri": firebase_secrets["auth_uri"],
        "token_uri": firebase_secrets["token_uri"],
        "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
    }
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- FONCTIONS FIRESTORE ---
def add_expense_to_firestore(category, amount, frequency, description, month, timestamp=None):
    """Ajoute une dépense à Firestore."""
    expense_ref = db.collection('expenses').document()
    expense_ref.set({
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Mois': month,
        'Timestamp': timestamp if timestamp else time.time()
    })

def add_revenue_to_firestore(source, amount, month, timestamp=None):
    """Ajoute un revenu à Firestore."""
    revenue_ref = db.collection('revenues').document()
    revenue_ref.set({
        'Source': source,
        'Montant': float(amount),
        'Mois': month,
        'Timestamp': timestamp if timestamp else time.time()
    })

def fetch_expenses_from_firestore():
    """Charge les dépenses depuis Firestore."""
    expenses_ref = db.collection('expenses')
    docs = expenses_ref.stream()
    expenses = []
    for doc in docs:
        expenses.append(doc.to_dict())
    return expenses

def fetch_revenues_from_firestore():
    """Charge les revenus depuis Firestore."""
    revenues_ref = db.collection('revenues')
    docs = revenues_ref.stream()
    revenues = []
    for doc in docs:
        revenues.append(doc.to_dict())
    return revenues

# --- INITIALISATION SESSION ---
if 'db_initialised' not in st.session_state:
    st.session_state.db_initialised = True
    st.session_state.expenses = fetch_expenses_from_firestore()
    st.session_state.revenues = fetch_revenues_from_firestore()

# --- VARIABLES ---
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

CATEGORIES_DEPENSES = ['Maison', 'Alimentation', 'Transport', 'Épargne', 
                       'Loisirs', 'Santé', 'Abonnements', 'Multimédia', 
                       'Enfants', 'Autre']

# --- INTERFACE ---
st.title("💰 Suivi du Budget Familial 2026")

# --- ONGLETS PRINCIPAUX ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Tableau de Bord", "➕ Ajouter des Données", "📤 Importer Excel", "📈 Analyses Détaillées"])

# ===== ONGLET 1: TABLEAU DE BORD =====
with tab1:
    # Sélection du/des mois
    col_filter1, col_filter2 = st.columns([3, 1])
    with col_filter1:
        selected_months = st.multiselect(
            "Sélectionner le(s) mois à analyser",
            options=MOIS,
            default=[MOIS[datetime.now().month - 1]] if datetime.now().month <= 12 else [MOIS[0]]
        )
    
    # Charger les données
    df_expenses = pd.DataFrame(st.session_state.expenses)
    df_revenues = pd.DataFrame(st.session_state.revenues)
    
    # Filtrer par mois sélectionnés
    if not df_expenses.empty and 'Mois' in df_expenses.columns and selected_months:
        df_expenses_filtered = df_expenses[df_expenses['Mois'].isin(selected_months)]
    else:
        df_expenses_filtered = df_expenses.copy() if not df_expenses.empty else pd.DataFrame()
    
    if not df_revenues.empty and 'Mois' in df_revenues.columns and selected_months:
        df_revenues_filtered = df_revenues[df_revenues['Mois'].isin(selected_months)]
    else:
        df_revenues_filtered = df_revenues.copy() if not df_revenues.empty else pd.DataFrame()
    
    # --- MÉTRIQUES PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenus = df_revenues_filtered['Montant'].sum() if not df_revenues_filtered.empty else 0
    total_depenses = df_expenses_filtered['Montant'].sum() if not df_expenses_filtered.empty else 0
    reste_a_vivre = total_revenus - total_depenses
    taux_epargne = (reste_a_vivre / total_revenus * 100) if total_revenus > 0 else 0
    
    with col1:
        st.metric("💶 Revenus Totaux", f"{total_revenus:,.0f} €")
    with col2:
        st.metric("💸 Dépenses Totales", f"{total_depenses:,.0f} €")
    with col3:
        st.metric("✨ Reste à Vivre", f"{reste_a_vivre:,.0f} €", 
                  delta=f"{taux_epargne:.1f}%" if reste_a_vivre >= 0 else None)
    with col4:
        pourcentage_depense = (total_depenses / total_revenus * 100) if total_revenus > 0 else 0
        st.metric("📊 % Revenu Dépensé", f"{pourcentage_depense:.0f}%")
    
    st.divider()
    
    # --- GRAPHIQUES PRINCIPAUX ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Revenus vs Dépenses")
        if not df_expenses_filtered.empty or not df_revenues_filtered.empty:
            fig_comparison = go.Figure(data=[
                go.Bar(name='Revenus', x=['Période sélectionnée'], y=[total_revenus], marker_color='#4472C4'),
                go.Bar(name='Dépenses', x=['Période sélectionnée'], y=[total_depenses], marker_color='#C5CAE9')
            ])
            fig_comparison.update_layout(barmode='group', height=350, showlegend=True)
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")
    
    with col_g2:
        st.subheader("Répartition des Dépenses")
        if not df_expenses_filtered.empty:
            df_cat = df_expenses_filtered.groupby('Catégories')['Montant'].sum().reset_index()
            fig_pie = px.pie(df_cat, values='Montant', names='Catégories',
                            color_discrete_sequence=px.colors.sequential.Blues_r,
                            hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Aucune dépense enregistrée")

# ===== ONGLET 2: AJOUTER DES DONNÉES =====
with tab2:
    col_add1, col_add2 = st.columns(2)
    
    # AJOUTER UN REVENU
    with col_add1:
        st.subheader("💰 Ajouter un Revenu")
        with st.form("revenue_form", clear_on_submit=True):
            rev_source = st.selectbox("Source de revenu", 
                                      options=['Salaire Principal', 'Salaire Conjoint', 
                                              'Primes', 'Revenus Complémentaires', 'Autre'])
            rev_amount = st.number_input("Montant (€)", min_value=0.01, step=50.0, key="rev_amt")
            rev_month = st.selectbox("Mois", options=MOIS, key="rev_month")
            
            if st.form_submit_button("💾 Enregistrer le Revenu"):
                add_revenue_to_firestore(rev_source, rev_amount, rev_month)
                st.session_state.revenues = fetch_revenues_from_firestore()
                st.success("✅ Revenu ajouté avec succès !")
                time.sleep(1)
                st.rerun()
    
    # AJOUTER UNE DÉPENSE
    with col_add2:
        st.subheader("💸 Ajouter une Dépense")
        with st.form("expense_form", clear_on_submit=True):
            exp_category = st.selectbox("Catégorie", options=CATEGORIES_DEPENSES)
            exp_amount = st.number_input("Montant (€)", min_value=0.01, step=5.0, key="exp_amt")
            exp_month = st.selectbox("Mois", options=MOIS, key="exp_month")
            exp_frequency = st.selectbox("Fréquence", 
                                        options=['Mensuel', 'Annuel', 'Trimestriel', 
                                                'Unique', 'Hebdomadaire'])
            exp_description = st.text_input("Description (facultatif)")
            
            if st.form_submit_button("💾 Enregistrer la Dépense"):
                add_expense_to_firestore(exp_category, exp_amount, exp_frequency, 
                                        exp_description, exp_month)
                st.session_state.expenses = fetch_expenses_from_firestore()
                st.success("✅ Dépense ajoutée avec succès !")
                time.sleep(1)
                st.rerun()

# ===== ONGLET 3: IMPORT EXCEL =====
with tab3:
    st.subheader("📤 Importer des données depuis Excel")
    
    col_imp1, col_imp2 = st.columns(2)
    
    with col_imp1:
        st.write("**Format attendu pour les DÉPENSES :**")
        st.code("Catégories | Montant | Fréquence | Mois | Description")
        uploaded_expenses = st.file_uploader("Importer les dépenses (.xlsx)", 
                                            type=['xlsx'], key="exp_upload")
        
        if uploaded_expenses:
            try:
                df_import_exp = pd.read_excel(uploaded_expenses)
                st.dataframe(df_import_exp.head())
                
                if st.button("Importer les dépenses", key="import_exp"):
                    for _, row in df_import_exp.iterrows():
                        add_expense_to_firestore(
                            row.get('Catégories', 'Autre'),
                            float(row.get('Montant', 0)),
                            row.get('Fréquence', 'Unique'),
                            row.get('Description', ''),
                            row.get('Mois', 'Janvier')
                        )
                    st.session_state.expenses = fetch_expenses_from_firestore()
                    st.success(f"✅ {len(df_import_exp)} dépenses importées !")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    
    with col_imp2:
        st.write("**Format attendu pour les REVENUS :**")
        st.code("Source | Montant | Mois")
        uploaded_revenues = st.file_uploader("Importer les revenus (.xlsx)", 
                                            type=['xlsx'], key="rev_upload")
        
        if uploaded_revenues:
            try:
                df_import_rev = pd.read_excel(uploaded_revenues)
                st.dataframe(df_import_rev.head())
                
                if st.button("Importer les revenus", key="import_rev"):
                    for _, row in df_import_rev.iterrows():
                        add_revenue_to_firestore(
                            row.get('Source', 'Autre'),
                            float(row.get('Montant', 0)),
                            row.get('Mois', 'Janvier')
                        )
                    st.session_state.revenues = fetch_revenues_from_firestore()
                    st.success(f"✅ {len(df_import_rev)} revenus importés !")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")

# ===== ONGLET 4: ANALYSES DÉTAILLÉES =====
with tab4:
    st.subheader("📈 Analyses Mensuelles Détaillées")
    
    # Préparer les données mensuelles
    if not df_expenses.empty and 'Mois' in df_expenses.columns:
        df_expenses['Mois_idx'] = df_expenses['Mois'].apply(lambda x: MOIS.index(x) if x in MOIS else 0)
        monthly_expenses = df_expenses.groupby('Mois')['Montant'].sum().reindex(MOIS, fill_value=0)
    else:
        monthly_expenses = pd.Series(0, index=MOIS)
    
    if not df_revenues.empty and 'Mois' in df_revenues.columns:
        df_revenues['Mois_idx'] = df_revenues['Mois'].apply(lambda x: MOIS.index(x) if x in MOIS else 0)
        monthly_revenues = df_revenues.groupby('Mois')['Montant'].sum().reindex(MOIS, fill_value=0)
    else:
        monthly_revenues = pd.Series(0, index=MOIS)
    
    # Graphique: Revenus et Dépenses par mois
    st.write("**Évolution Revenus vs Dépenses (2026)**")
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=MOIS, y=monthly_revenues, name='Revenus', marker_color='#4472C4'))
    fig_monthly.add_trace(go.Bar(x=MOIS, y=monthly_expenses, name='Dépenses', marker_color='#C5CAE9'))
    fig_monthly.update_layout(barmode='group', height=400, xaxis_title="Mois", yaxis_title="Montant (€)")
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    st.divider()
    
    # Graphique: Total des dépenses par catégorie (toute l'année)
    st.write("**Total des Dépenses par Catégorie (2026)**")
    if not df_expenses.empty:
        df_cat_total = df_expenses.groupby('Catégories')['Montant'].sum().sort_values(ascending=False).reset_index()
        fig_cat_bar = px.bar(df_cat_total, x='Catégories', y='Montant', 
                            color='Montant', color_continuous_scale='Blues')
        fig_cat_bar.update_layout(height=400, xaxis_title="Catégorie", yaxis_title="Total (€)")
        st.plotly_chart(fig_cat_bar, use_container_width=True)
    else:
        st.info("Aucune dépense à analyser")
    
    st.divider()
    
    # Tableau récapitulatif mensuel
    st.write("**Récapitulatif Mensuel**")
    recap_data = []
    for mois in MOIS:
        rev = monthly_revenues[mois]
        dep = monthly_expenses[mois]
        solde = rev - dep
        recap_data.append({
            'Mois': mois,
            'Revenus (€)': f"{rev:,.0f}",
            'Dépenses (€)': f"{dep:,.0f}",
            'Solde (€)': f"{solde:,.0f}",
            '% Dépensé': f"{(dep/rev*100):.0f}%" if rev > 0 else "N/A"
        })
    
    df_recap = pd.DataFrame(recap_data)
    st.dataframe(df_recap, use_container_width=True, hide_index=True)

st.markdown("""
<style>
.stApp { padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)
