import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le dossier services au path
current_dir = Path(__file__).parent.parent
services_dir = current_dir / "services"
sys.path.insert(0, str(services_dir))

# Imports des services
try:
    from firebase import (init_firebase, get_notifications, mark_notification_as_read,
                         get_unread_notifications_count)
    from budget_service import (add_expense, add_revenue, fetch_expenses, fetch_revenues,
                                delete_expense, delete_revenue, CATEGORIES_DEPENSES)
    from theme_manager import apply_theme
    SERVICES_OK = True
except ImportError as e:
    st.error(f"⚠️ Erreur d'import: {str(e)}")
    SERVICES_OK = False

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

# Initialiser Firebase
if SERVICES_OK:
    init_firebase()
    # Appliquer le thème de l'utilisateur
    apply_theme(st.session_state.user_profile)
else:
    # Thème par défaut
    from theme_manager import apply_theme
    apply_theme(None)

# --- STYLES ---
st.markdown("""
<style>
    /* Styles additionnels spécifiques au module Budget */
    .budget-header {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- VARIABLES ---
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

# --- EN-TÊTE ---
col_back, col_title, col_notif = st.columns([1, 4, 1])

with col_back:
    if st.button("← Retour"):
        st.switch_page("streamlit_app.py")

with col_title:
    st.title("💰 Budget Familial")
    st.write(f"**Connecté:** {st.session_state.user_profile}")

with col_notif:
    if SERVICES_OK:
        unread_count = get_unread_notifications_count()
        
        if st.button(f"🔔 ({unread_count})" if unread_count > 0 else "🔔"):
            st.session_state.show_notifications = not st.session_state.get('show_notifications', False)
        
        # Panel de notifications
        if st.session_state.get('show_notifications', False):
            st.markdown("<div style='background-color: #2d3142; border-radius: 10px; padding: 15px; margin-top: 10px; max-height: 300px; overflow-y: auto;'>", unsafe_allow_html=True)
            notifications = get_notifications()
            
            if notifications:
                for notif in notifications[:5]:  # Afficher les 5 dernières
                    if notif.get('module') in ['budget', 'general']:
                        timestamp = notif.get('timestamp', 0)
                        time_ago = datetime.fromtimestamp(timestamp).strftime("%d/%m %H:%M")
                        border_color = "#667eea" if notif.get('read', False) else "#ff4444"
                        
                        st.markdown(f"""
                        <div style='background-color: #1f2230; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {border_color};'>
                            <div style='font-weight: bold; color: #ffffff; font-size: 14px;'>{notif.get('title', '')}</div>
                            <div style='color: #a0a0a0; font-size: 12px;'>{notif.get('message', '')}</div>
                            <div style='color: #707070; font-size: 11px; margin-top: 5px;'>{time_ago}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if not notif.get('read', False):
                            mark_notification_as_read(notif['doc_id'])
            else:
                st.info("Aucune notification")
            
            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- CHARGEMENT DES DONNÉES DEPUIS FIREBASE ---
if SERVICES_OK:
    if 'expenses' not in st.session_state or st.button("🔄 Actualiser", key="refresh_data"):
        with st.spinner("Chargement des données..."):
            st.session_state.expenses = fetch_expenses()
            st.session_state.revenues = fetch_revenues()
            st.success("✅ Données chargées !")
            time.sleep(0.5)
            st.rerun()
else:
    # Mode hors ligne
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    if 'revenues' not in st.session_state:
        st.session_state.revenues = []
    st.warning("⚠️ Mode hors ligne - Les données ne seront pas sauvegardées")

if 'selected_year' not in st.session_state:
    st.session_state.selected_year = datetime.now().year

# --- ONGLETS ---
tabs = st.tabs(["📊 Tableau de Bord", "📋 Revenus", "📋 Dépenses"])

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
    taux_epargne = (reste_a_vivre / total_revenus * 100) if total_revenus > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
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
        st.metric("✨ Reste à Vivre", f"{reste_a_vivre:,.0f} €", 
                 delta=f"{taux_epargne:.1f}%" if reste_a_vivre >= 0 else None)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        pourcentage_depense = (total_depenses / total_revenus * 100) if total_revenus > 0 else 0
        st.metric("📊 % Dépensé", f"{pourcentage_depense:.0f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Graphiques
    if not df_expenses_filtered.empty or not df_revenues_filtered.empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("Revenus vs Dépenses")
            fig = go.Figure(data=[
                go.Bar(name='Revenus', x=['Total'], y=[total_revenus], 
                      marker_color='#667eea', text=[f'{total_revenus:,.0f}€'], textposition='outside'),
                go.Bar(name='Dépenses', x=['Total'], y=[total_depenses], 
                      marker_color='#764ba2', text=[f'{total_depenses:,.0f}€'], textposition='outside')
            ])
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', 
                            paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_g2:
            if not df_expenses_filtered.empty:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.subheader("Répartition des Dépenses")
                df_cat = df_expenses_filtered.groupby('Catégories')['Montant'].sum().reset_index()
                fig_pie = px.pie(df_cat, values='Montant', names='Catégories', hole=0.4,
                               color_discrete_sequence=px.colors.sequential.Purples_r)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', 
                                     paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Aucune donnée disponible. Ajoutez des revenus ou dépenses !")

# ===== ONGLET 2: REVENUS =====
with tabs[1]:
    st.subheader(f"📋 Gestion des Revenus - {st.session_state.selected_year}")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter un revenu", expanded=False):
        with st.form("add_revenue", clear_on_submit=True):
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
                if SERVICES_OK:
                    success = add_revenue(rev_source, rev_amount, rev_month, rev_year, 
                                        st.session_state.user_profile)
                    if success:
                        st.success("✅ Revenu ajouté avec succès !")
                        time.sleep(1)
                        st.rerun()
                else:
                    # Mode hors ligne
                    st.session_state.revenues.append({
                        'Source': rev_source,
                        'Montant': float(rev_amount),
                        'Mois': rev_month,
                        'Année': int(rev_year),
                        'Utilisateur': st.session_state.user_profile
                    })
                    st.success("✅ Revenu ajouté (mode hors ligne)")
                    st.rerun()
    
    # Affichage des revenus
    if st.session_state.revenues:
        df_rev = pd.DataFrame(st.session_state.revenues)
        if 'Année' in df_rev.columns:
            df_rev_year = df_rev[df_rev['Année'] == st.session_state.selected_year]
            
            if not df_rev_year.empty:
                st.dataframe(df_rev_year[['Source', 'Montant', 'Mois', 'Utilisateur']], 
                            use_container_width=True, hide_index=True)
            else:
                st.info(f"Aucun revenu pour {st.session_state.selected_year}")
        else:
            st.dataframe(df_rev, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun revenu enregistré")

# ===== ONGLET 3: DÉPENSES =====
with tabs[2]:
    st.subheader(f"📋 Gestion des Dépenses - {st.session_state.selected_year}")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter une dépense", expanded=False):
        with st.form("add_expense", clear_on_submit=True):
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
                if SERVICES_OK:
                    success = add_expense(exp_category, exp_amount, exp_frequency, 
                                        exp_description, exp_month, exp_year, 
                                        st.session_state.user_profile)
                    if success:
                        st.success("✅ Dépense ajoutée avec succès !")
                        time.sleep(1)
                        st.rerun()
                else:
                    # Mode hors ligne
                    st.session_state.expenses.append({
                        'Catégories': exp_category,
                        'Montant': float(exp_amount),
                        'Fréquence': exp_frequency,
                        'Description': exp_description,
                        'Mois': exp_month,
                        'Année': int(exp_year),
                        'Utilisateur': st.session_state.user_profile
                    })
                    st.success("✅ Dépense ajoutée (mode hors ligne)")
                    st.rerun()
    
    # Affichage des dépenses
    if st.session_state.expenses:
        df_exp = pd.DataFrame(st.session_state.expenses)
        if 'Année' in df_exp.columns:
            df_exp_year = df_exp[df_exp['Année'] == st.session_state.selected_year]
            
            if not df_exp_year.empty:
                st.dataframe(df_exp_year[['Catégories', 'Montant', 'Mois', 'Description', 'Utilisateur']], 
                            use_container_width=True, hide_index=True)
            else:
                st.info(f"Aucune dépense pour {st.session_state.selected_year}")
        else:
            st.dataframe(df_exp, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune dépense enregistrée")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #707070; font-size: 14px; padding: 20px;'>
    <p>Module Budget - Famileasy v1.0.0</p>
</div>
""", unsafe_allow_html=True)