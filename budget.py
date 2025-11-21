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
def add_expense_to_firestore(category, amount, frequency, description, month, year, timestamp=None):
    """Ajoute une dépense à Firestore."""
    expense_ref = db.collection('expenses').document()
    expense_ref.set({
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Mois': month,
        'Année': int(year),
        'Timestamp': timestamp if timestamp else time.time()
    })

def add_revenue_to_firestore(source, amount, month, year, timestamp=None):
    """Ajoute un revenu à Firestore."""
    revenue_ref = db.collection('revenues').document()
    revenue_ref.set({
        'Source': source,
        'Montant': float(amount),
        'Mois': month,
        'Année': int(year),
        'Timestamp': timestamp if timestamp else time.time()
    })

def update_expense_in_firestore(doc_id, category, amount, frequency, description, month, year):
    """Met à jour une dépense dans Firestore."""
    expense_ref = db.collection('expenses').document(doc_id)
    expense_ref.update({
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Mois': month,
        'Année': int(year)
    })

def update_revenue_in_firestore(doc_id, source, amount, month, year):
    """Met à jour un revenu dans Firestore."""
    revenue_ref = db.collection('revenues').document(doc_id)
    revenue_ref.update({
        'Source': source,
        'Montant': float(amount),
        'Mois': month,
        'Année': int(year)
    })

def delete_expense_from_firestore(doc_id):
    """Supprime une dépense de Firestore."""
    db.collection('expenses').document(doc_id).delete()

def delete_revenue_from_firestore(doc_id):
    """Supprime un revenu de Firestore."""
    db.collection('revenues').document(doc_id).delete()

def fetch_expenses_from_firestore():
    """Charge les dépenses depuis Firestore avec leurs IDs."""
    expenses_ref = db.collection('expenses')
    docs = expenses_ref.stream()
    expenses = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        expenses.append(data)
    return expenses

def fetch_revenues_from_firestore():
    """Charge les revenus depuis Firestore avec leurs IDs."""
    revenues_ref = db.collection('revenues')
    docs = revenues_ref.stream()
    revenues = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        revenues.append(data)
    return revenues

# --- INITIALISATION SESSION ---
if 'db_initialised' not in st.session_state:
    st.session_state.db_initialised = True
    st.session_state.expenses = fetch_expenses_from_firestore()
    st.session_state.revenues = fetch_revenues_from_firestore()

# --- VARIABLES ---
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

MOIS_SHORT = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
              'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

CATEGORIES_DEPENSES = [
    'Compte Perso - Souliman',
    'Compte Perso - Margaux',
    'Essence',
    'Loyer',
    'Forfait Internet',
    'Forfait Mobile',
    'Crédit Voiture',
    'Frais Bourso (Voitures, Maison, Hopital...)',
    'Crédit Consomation',
    'Engie (chauffage + élec)',
    'Veolia (eau)',
    'Assurance Maison',
    'Frais Voiture (Réparation, Assurance...)',
    'Anniversaires (Fêtes Noël, pacques...)',
    'Olga',
    'Épargne',
    'École Clémence',
    'Épargne Clémence',
    'Marge compte',
    'Courses',
    'Autre'
]

ANNEES = list(range(2020, 2031))

# --- INTERFACE ---
st.title("💰 Suivi du Budget Familial")

# Sélection de l'année (en haut de la page)
col_year, col_space = st.columns([1, 3])
with col_year:
    selected_year = st.selectbox("📅 Année", options=ANNEES, index=ANNEES.index(datetime.now().year))

# --- ONGLETS PRINCIPAUX ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Tableau de Bord", "📋 Tableau Revenus", "📋 Tableau Dépenses", "➕ Ajouter", "📤 Importer Excel"])

# ===== ONGLET 1: TABLEAU DE BORD =====
with tab1:
    # Sélection du/des mois
    selected_months = st.multiselect(
        "Sélectionner le(s) mois à analyser",
        options=MOIS,
        default=MOIS
    )
    
    # Charger les données
    df_expenses = pd.DataFrame(st.session_state.expenses)
    df_revenues = pd.DataFrame(st.session_state.revenues)
    
    # Filtrer par année et mois
    if not df_expenses.empty and 'Mois' in df_expenses.columns and 'Année' in df_expenses.columns:
        df_expenses_filtered = df_expenses[
            (df_expenses['Année'] == selected_year) & 
            (df_expenses['Mois'].isin(selected_months))
        ]
    else:
        df_expenses_filtered = pd.DataFrame()
    
    if not df_revenues.empty and 'Mois' in df_revenues.columns and 'Année' in df_revenues.columns:
        df_revenues_filtered = df_revenues[
            (df_revenues['Année'] == selected_year) & 
            (df_revenues['Mois'].isin(selected_months))
        ]
    else:
        df_revenues_filtered = pd.DataFrame()
    
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
    
    # Graphique mensuel
    st.subheader(f"Évolution Mensuelle - {selected_year}")
    
    if not df_expenses.empty and 'Année' in df_expenses.columns:
        monthly_expenses = df_expenses[df_expenses['Année'] == selected_year].groupby('Mois')['Montant'].sum().reindex(MOIS, fill_value=0)
    else:
        monthly_expenses = pd.Series(0, index=MOIS)
    
    if not df_revenues.empty and 'Année' in df_revenues.columns:
        monthly_revenues = df_revenues[df_revenues['Année'] == selected_year].groupby('Mois')['Montant'].sum().reindex(MOIS, fill_value=0)
    else:
        monthly_revenues = pd.Series(0, index=MOIS)
    
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=MOIS_SHORT, y=monthly_revenues, name='Revenus', marker_color='#4472C4'))
    fig_monthly.add_trace(go.Bar(x=MOIS_SHORT, y=monthly_expenses, name='Dépenses', marker_color='#C5CAE9'))
    fig_monthly.update_layout(barmode='group', height=400, xaxis_title="Mois", yaxis_title="Montant (€)")
    st.plotly_chart(fig_monthly, use_container_width=True)

# ===== ONGLET 2: TABLEAU REVENUS =====
with tab2:
    st.subheader(f"📋 Tableau des Revenus - {selected_year}")
    
    if not df_revenues.empty and 'Année' in df_revenues.columns:
        df_rev_year = df_revenues[df_revenues['Année'] == selected_year].copy()
        
        if not df_rev_year.empty:
            # Créer un tableau pivot
            pivot_data = []
            sources = df_rev_year['Source'].unique()
            
            for source in sources:
                row_data = {'Élément': source}
                df_source = df_rev_year[df_rev_year['Source'] == source]
                
                total = 0
                for mois in MOIS_SHORT:
                    mois_full = MOIS[MOIS_SHORT.index(mois)]
                    montant = df_source[df_source['Mois'] == mois_full]['Montant'].sum()
                    row_data[mois] = f"{montant:,.0f} €" if montant > 0 else "0 €"
                    total += montant
                
                row_data['Total'] = f"{total:,.0f} €"
                row_data['Moyen'] = f"{total/12:,.0f} €"
                pivot_data.append(row_data)
            
            # Ligne Total
            total_row = {'Élément': '**Total**'}
            grand_total = 0
            for mois in MOIS_SHORT:
                mois_full = MOIS[MOIS_SHORT.index(mois)]
                montant = df_rev_year[df_rev_year['Mois'] == mois_full]['Montant'].sum()
                total_row[mois] = f"**{montant:,.0f} €**"
                grand_total += montant
            total_row['Total'] = f"**{grand_total:,.0f} €**"
            total_row['Moyen'] = f"**{grand_total/12:,.0f} €**"
            pivot_data.append(total_row)
            
            df_pivot = pd.DataFrame(pivot_data)
            st.dataframe(df_pivot, use_container_width=True, hide_index=True)
            
            # Section Modification/Suppression
            st.divider()
            st.write("**Modifier ou Supprimer un Revenu**")
            
            # Préparer les options pour le selectbox
            df_rev_display = df_rev_year[['Source', 'Montant', 'Mois', 'doc_id']].copy()
            df_rev_display['Display'] = df_rev_display.apply(
                lambda x: f"{x['Source']} - {x['Montant']:.0f}€ - {x['Mois']}", axis=1
            )
            
            selected_rev = st.selectbox(
                "Sélectionner un revenu à modifier/supprimer",
                options=df_rev_display['Display'].tolist(),
                key="select_rev"
            )
            
            if selected_rev:
                idx = df_rev_display[df_rev_display['Display'] == selected_rev].index[0]
                rev_data = df_rev_year.loc[idx]
                
                col_mod, col_del = st.columns([3, 1])
                
                with col_mod:
                    with st.form("edit_revenue_form"):
                        st.write("**Modifier ce revenu**")
                        new_source = st.selectbox("Source", 
                                                  options=['Salaire Principal', 'Salaire Conjoint', 
                                                          'Primes', 'Revenus Complémentaires', 'Autre'],
                                                  index=['Salaire Principal', 'Salaire Conjoint', 
                                                        'Primes', 'Revenus Complémentaires', 'Autre'].index(rev_data['Source']) 
                                                        if rev_data['Source'] in ['Salaire Principal', 'Salaire Conjoint', 
                                                        'Primes', 'Revenus Complémentaires', 'Autre'] else 0)
                        new_amount = st.number_input("Montant", value=float(rev_data['Montant']), step=10.0)
                        new_month = st.selectbox("Mois", options=MOIS, index=MOIS.index(rev_data['Mois']))
                        
                        if st.form_submit_button("💾 Enregistrer les modifications"):
                            update_revenue_in_firestore(rev_data['doc_id'], new_source, new_amount, new_month, selected_year)
                            st.session_state.revenues = fetch_revenues_from_firestore()
                            st.success("✅ Revenu modifié !")
                            time.sleep(1)
                            st.rerun()
                
                with col_del:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Supprimer", key="del_rev", type="secondary"):
                        delete_revenue_from_firestore(rev_data['doc_id'])
                        st.session_state.revenues = fetch_revenues_from_firestore()
                        st.success("✅ Revenu supprimé !")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info(f"Aucun revenu enregistré pour {selected_year}")
    else:
        st.info("Aucun revenu enregistré")

# ===== ONGLET 3: TABLEAU DÉPENSES =====
with tab3:
    st.subheader(f"📋 Tableau des Dépenses - {selected_year}")
    
    if not df_expenses.empty and 'Année' in df_expenses.columns:
        df_exp_year = df_expenses[df_expenses['Année'] == selected_year].copy()
        
        if not df_exp_year.empty:
            # Créer un tableau pivot
            pivot_data = []
            categories = df_exp_year['Catégories'].unique()
            
            for cat in categories:
                row_data = {'Élément': cat}
                df_cat = df_exp_year[df_exp_year['Catégories'] == cat]
                
                total = 0
                for mois in MOIS_SHORT:
                    mois_full = MOIS[MOIS_SHORT.index(mois)]
                    montant = df_cat[df_cat['Mois'] == mois_full]['Montant'].sum()
                    row_data[mois] = f"{montant:,.0f} €" if montant > 0 else "0 €"
                    total += montant
                
                row_data['Total'] = f"{total:,.0f} €"
                row_data['Moyen'] = f"{total/12:,.0f} €"
                pivot_data.append(row_data)
            
            # Ligne Total
            total_row = {'Élément': '**Total**'}
            grand_total = 0
            for mois in MOIS_SHORT:
                mois_full = MOIS[MOIS_SHORT.index(mois)]
                montant = df_exp_year[df_exp_year['Mois'] == mois_full]['Montant'].sum()
                total_row[mois] = f"**{montant:,.0f} €**"
                grand_total += montant
            total_row['Total'] = f"**{grand_total:,.0f} €**"
            total_row['Moyen'] = f"**{grand_total/12:,.0f} €**"
            pivot_data.append(total_row)
            
            df_pivot = pd.DataFrame(pivot_data)
            st.dataframe(df_pivot, use_container_width=True, hide_index=True)
            
            # Section Modification/Suppression
            st.divider()
            st.write("**Modifier ou Supprimer une Dépense**")
            
            # Préparer les options
            df_exp_display = df_exp_year[['Catégories', 'Montant', 'Mois', 'Description', 'doc_id']].copy()
            df_exp_display['Display'] = df_exp_display.apply(
                lambda x: f"{x['Catégories']} - {x['Montant']:.0f}€ - {x['Mois']} - {x['Description']}", axis=1
            )
            
            selected_exp = st.selectbox(
                "Sélectionner une dépense à modifier/supprimer",
                options=df_exp_display['Display'].tolist(),
                key="select_exp"
            )
            
            if selected_exp:
                idx = df_exp_display[df_exp_display['Display'] == selected_exp].index[0]
                exp_data = df_exp_year.loc[idx]
                
                col_mod, col_del = st.columns([3, 1])
                
                with col_mod:
                    with st.form("edit_expense_form"):
                        st.write("**Modifier cette dépense**")
                        new_cat = st.selectbox("Catégorie", options=CATEGORIES_DEPENSES, 
                                              index=CATEGORIES_DEPENSES.index(exp_data['Catégories']) 
                                              if exp_data['Catégories'] in CATEGORIES_DEPENSES else 0)
                        new_amount = st.number_input("Montant", value=float(exp_data['Montant']), step=5.0)
                        new_month = st.selectbox("Mois", options=MOIS, index=MOIS.index(exp_data['Mois']))
                        new_freq = st.selectbox("Fréquence", 
                                               options=['Mensuel', 'Annuel', 'Trimestriel', 'Unique', 'Hebdomadaire'],
                                               index=['Mensuel', 'Annuel', 'Trimestriel', 'Unique', 'Hebdomadaire'].index(exp_data['Fréquence'])
                                               if exp_data['Fréquence'] in ['Mensuel', 'Annuel', 'Trimestriel', 'Unique', 'Hebdomadaire'] else 0)
                        new_desc = st.text_input("Description", value=exp_data.get('Description', ''))
                        
                        if st.form_submit_button("💾 Enregistrer les modifications"):
                            update_expense_in_firestore(exp_data['doc_id'], new_cat, new_amount, new_freq, new_desc, new_month, selected_year)
                            st.session_state.expenses = fetch_expenses_from_firestore()
                            st.success("✅ Dépense modifiée !")
                            time.sleep(1)
                            st.rerun()
                
                with col_del:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Supprimer", key="del_exp", type="secondary"):
                        delete_expense_from_firestore(exp_data['doc_id'])
                        st.session_state.expenses = fetch_expenses_from_firestore()
                        st.success("✅ Dépense supprimée !")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info(f"Aucune dépense enregistrée pour {selected_year}")
    else:
        st.info("Aucune dépense enregistrée")

# ===== ONGLET 4: AJOUTER DES DONNÉES =====
with tab4:
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
            rev_year = st.number_input("Année", min_value=2020, max_value=2030, value=selected_year, key="rev_year")
            
            if st.form_submit_button("💾 Enregistrer le Revenu"):
                add_revenue_to_firestore(rev_source, rev_amount, rev_month, rev_year)
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
            exp_year = st.number_input("Année", min_value=2020, max_value=2030, value=selected_year, key="exp_year")
            exp_frequency = st.selectbox("Fréquence", 
                                        options=['Mensuel', 'Annuel', 'Trimestriel', 
                                                'Unique', 'Hebdomadaire'])
            exp_description = st.text_input("Description (facultatif)")
            
            if st.form_submit_button("💾 Enregistrer la Dépense"):
                add_expense_to_firestore(exp_category, exp_amount, exp_frequency, 
                                        exp_description, exp_month, exp_year)
                st.session_state.expenses = fetch_expenses_from_firestore()
                st.success("✅ Dépense ajoutée avec succès !")
                time.sleep(1)
                st.rerun()

# ===== ONGLET 5: IMPORT EXCEL =====
with tab5:
    st.subheader("📤 Importer des données depuis Excel")
    
    col_imp1, col_imp2 = st.columns(2)
    
    with col_imp1:
        st.write("**Format attendu pour les DÉPENSES :**")
        st.code("Catégories | Montant | Fréquence | Mois | Année | Description")
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
                            row.get('Mois', 'Janvier'),
                            int(row.get('Année', selected_year))
                        )
                    st.session_state.expenses = fetch_expenses_from_firestore()
                    st.success(f"✅ {len(df_import_exp)} dépenses importées !")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    
    with col_imp2:
        st.write("**Format attendu pour les REVENUS :**")
        st.code("Source | Montant | Mois | Année")
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
                            row.get('Mois', 'Janvier'),
                            int(row.get('Année', selected_year))
                        )
                    st.session_state.revenues = fetch_revenues_from_firestore()
                    st.success(f"✅ {len(df_import_rev)} revenus importés !")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")

st.markdown("""
<style>
.stApp { padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)
