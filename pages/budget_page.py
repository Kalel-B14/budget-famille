import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Budget - Famileasy",
    page_icon="💰",
    layout="wide"
)

# Vérifier l'authentification
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.error("⚠️ Veuillez vous connecter")
    if st.button("Retour à l'accueil"):
        st.switch_page("streamlit_app.py")
    st.stop()

# --- STYLES ---
st.markdown("""
<style>
    .stApp {
        background-color: #1a1d24;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- VARIABLES ---
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

CATEGORIES_DEPENSES = [
    'Compte Perso - Souliman', 'Compte Perso - Margaux', 'Essence', 'Loyer',
    'Forfait Internet', 'Forfait Mobile', 'Crédit Voiture',
    'Frais Bourso (Voitures, Maison, Hopital...)', 'Crédit Consomation',
    'Engie (chauffage + élec)', 'Veolia (eau)', 'Assurance Maison',
    'Frais Voiture (Réparation, Assurance...)', 'Anniversaires (Fêtes Noël, pacques...)',
    'Olga', 'Épargne', 'École Clémence', 'Épargne Clémence', 'Marge compte',
    'Courses', 'Autre'
]

# --- EN-TÊTE ---
col_back, col_title = st.columns([1, 5])

with col_back:
    if st.button("← Retour"):
        st.switch_page("streamlit_app.py")

with col_title:
    st.title("💰 Budget Familial")
    st.write(f"**Connecté:** {st.session_state.user_profile}")

st.divider()

# --- INITIALISATION DES DONNÉES ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

if 'revenues' not in st.session_state:
    st.session_state.revenues = []

if 'selected_year' not in st.session_state:
    st.session_state.selected_year = datetime.now().year

# --- ONGLETS ---
tabs = st.tabs(["📊 Tableau de Bord", "📋 Revenus", "📋 Dépenses", "📤 Importer"])

# ===== ONGLET 1: TABLEAU DE BORD =====
with tabs[0]:
    # Sélection de l'année
    selected_year = st.selectbox("📅 Année", options=list(range(2020, 2031)), 
                                 index=list(range(2020, 2031)).index(st.session_state.selected_year))
    
    st.session_state.selected_year = selected_year
    
    # Préparer les données
    df_expenses = pd.DataFrame(st.session_state.expenses)
    df_revenues = pd.DataFrame(st.session_state.revenues)
    
    # Filtrer par année
    if not df_expenses.empty and 'Année' in df_expenses.columns:
        df_expenses_filtered = df_expenses[df_expenses['Année'] == selected_year]
    else:
        df_expenses_filtered = pd.DataFrame()
    
    if not df_revenues.empty and 'Année' in df_revenues.columns:
        df_revenues_filtered = df_revenues[df_revenues['Année'] == selected_year]
    else:
        df_revenues_filtered = pd.DataFrame()
    
    # Métriques
    total_revenus = df_revenues_filtered['Montant'].sum() if not df_revenues_filtered.empty else 0
    total_depenses = df_expenses_filtered['Montant'].sum() if not df_expenses_filtered.empty else 0
    reste_a_vivre = total_revenus - total_depenses
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("💶 Revenus Totaux", f"{total_revenus:,.0f} €")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("💸 Dépenses Totales", f"{total_depenses:,.0f} €")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("✨ Reste à Vivre", f"{reste_a_vivre:,.0f} €")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Graphiques
    if not df_expenses_filtered.empty or not df_revenues_filtered.empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Revenus vs Dépenses")
            fig = go.Figure(data=[
                go.Bar(name='Revenus', x=['Total'], y=[total_revenus], marker_color='#667eea'),
                go.Bar(name='Dépenses', x=['Total'], y=[total_depenses], marker_color='#764ba2')
            ])
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', 
                            paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
            st.plotly_chart(fig, use_container_width=True)
        
        with col_g2:
            if not df_expenses_filtered.empty:
                st.subheader("Répartition des Dépenses")
                df_cat = df_expenses_filtered.groupby('Catégories')['Montant'].sum().reset_index()
                fig_pie = px.pie(df_cat, values='Montant', names='Catégories', hole=0.4)
                fig_pie.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', 
                                     paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Aucune donnée disponible. Ajoutez des revenus ou dépenses !")

# ===== ONGLET 2: REVENUS =====
with tabs[1]:
    st.subheader(f"📋 Gestion des Revenus - {st.session_state.selected_year}")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter un revenu"):
        with st.form("add_revenue"):
            col1, col2 = st.columns(2)
            with col1:
                rev_source = st.selectbox("Source", 
                    options=['Salaire Principal', 'Salaire Conjoint', 'Primes', 'Autre'])
                rev_amount = st.number_input("Montant (€)", min_value=0.01, step=50.0)
            with col2:
                rev_month = st.selectbox("Mois", options=MOIS)
                rev_year = st.number_input("Année", min_value=2020, max_value=2030, 
                                          value=st.session_state.selected_year)
            
            if st.form_submit_button("💾 Enregistrer"):
                new_revenue = {
                    'Source': rev_source,
                    'Montant': float(rev_amount),
                    'Mois': rev_month,
                    'Année': int(rev_year),
                    'Utilisateur': st.session_state.user_profile,
                    'Timestamp': time.time()
                }
                st.session_state.revenues.append(new_revenue)
                st.success("✅ Revenu ajouté !")
                st.rerun()
    
    # Affichage des revenus
    if st.session_state.revenues:
        df_rev = pd.DataFrame(st.session_state.revenues)
        df_rev_year = df_rev[df_rev['Année'] == st.session_state.selected_year]
        
        if not df_rev_year.empty:
            st.dataframe(df_rev_year[['Source', 'Montant', 'Mois', 'Utilisateur']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucun revenu pour {st.session_state.selected_year}")
    else:
        st.info("Aucun revenu enregistré")

# ===== ONGLET 3: DÉPENSES =====
with tabs[2]:
    st.subheader(f"📋 Gestion des Dépenses - {st.session_state.selected_year}")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter une dépense"):
        with st.form("add_expense"):
            col1, col2 = st.columns(2)
            with col1:
                exp_category = st.selectbox("Catégorie", options=CATEGORIES_DEPENSES)
                exp_amount = st.number_input("Montant (€)", min_value=0.01, step=5.0)
                exp_month = st.selectbox("Mois", options=MOIS)
            with col2:
                exp_year = st.number_input("Année", min_value=2020, max_value=2030, 
                                          value=st.session_state.selected_year)
                exp_frequency = st.selectbox("Fréquence", 
                    options=['Mensuel', 'Annuel', 'Unique'])
                exp_description = st.text_input("Description")
            
            if st.form_submit_button("💾 Enregistrer"):
                new_expense = {
                    'Catégories': exp_category,
                    'Montant': float(exp_amount),
                    'Fréquence': exp_frequency,
                    'Description': exp_description,
                    'Mois': exp_month,
                    'Année': int(exp_year),
                    'Utilisateur': st.session_state.user_profile,
                    'Timestamp': time.time()
                }
                st.session_state.expenses.append(new_expense)
                st.success("✅ Dépense ajoutée !")
                st.rerun()
    
    # Affichage des dépenses
    if st.session_state.expenses:
        df_exp = pd.DataFrame(st.session_state.expenses)
        df_exp_year = df_exp[df_exp['Année'] == st.session_state.selected_year]
        
        if not df_exp_year.empty:
            st.dataframe(df_exp_year[['Catégories', 'Montant', 'Mois', 'Description', 'Utilisateur']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucune dépense pour {st.session_state.selected_year}")
    else:
        st.info("Aucune dépense enregistrée")

# ===== ONGLET 4: IMPORT =====
with tabs[3]:
    st.subheader("📤 Importer des données depuis Excel")
    st.info("⚠️ Import Excel disponible prochainement avec Firebase")
    
    st.write("**Format attendu pour les dépenses :**")
    st.code("Catégorie | Montant | Fréquence | Mois | Année | Description")
    
    st.write("**Format attendu pour les revenus :**")
    st.code("Source | Montant | Mois | Année")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #707070; font-size: 14px; padding: 20px;'>
    <p>Module Budget - Famileasy v1.0.0</p>
</div>
""", unsafe_allow_html=True)
