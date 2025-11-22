import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le dossier services au path
sys.path.append(str(Path(__file__).parent.parent / "services"))

from firebase import (init_firebase, load_profile_image, add_notification,
                      get_notifications, mark_notification_as_read, get_unread_notifications_count,
                      save_user_preferences, load_user_preferences)
from utils import apply_dark_theme, check_user_authentication, create_module_header
from budget_service import (add_expense, add_revenue, update_expense, update_revenue,
                            delete_expense, delete_revenue, fetch_expenses, fetch_revenues,
                            import_expenses_from_excel, import_revenues_from_excel)

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Budget - Famileasy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialiser Firebase
init_firebase()

# Vérifier l'authentification
check_user_authentication()

# Appliquer le thème
apply_dark_theme()

# --- VARIABLES ---
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

MOIS_SHORT = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
              'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

CATEGORIES_DEPENSES = [
    'Compte Perso - Souliman', 'Compte Perso - Margaux', 'Essence', 'Loyer',
    'Forfait Internet', 'Forfait Mobile', 'Crédit Voiture',
    'Frais Bourso (Voitures, Maison, Hopital...)', 'Crédit Consomation',
    'Engie (chauffage + élec)', 'Veolia (eau)', 'Assurance Maison',
    'Frais Voiture (Réparation, Assurance...)', 'Anniversaires (Fêtes Noël, pacques...)',
    'Olga', 'Épargne', 'École Clémence', 'Épargne Clémence', 'Marge compte',
    'Courses', 'Autre'
]

ANNEES = list(range(2020, 2031))

# --- INITIALISATION SESSION ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = fetch_expenses()

if 'revenues' not in st.session_state:
    st.session_state.revenues = fetch_revenues()

if 'selected_year' not in st.session_state:
    # Charger les préférences sauvegardées
    prefs = load_user_preferences(st.session_state.user_profile)
    if prefs and 'budget_year' in prefs:
        st.session_state.selected_year = prefs['budget_year']
    else:
        st.session_state.selected_year = datetime.now().year

if 'selected_months' not in st.session_state:
    prefs = load_user_preferences(st.session_state.user_profile)
    if prefs and 'budget_months' in prefs:
        st.session_state.selected_months = prefs['budget_months']
    else:
        st.session_state.selected_months = MOIS

# --- EN-TÊTE ---
col_back, col_title, col_notif, col_year = st.columns([1, 3, 1, 1])

with col_back:
    if st.button("← Retour", key="back_home"):
        st.switch_page("Home.py")

with col_title:
    create_module_header("Budget Familial", "💰")

with col_notif:
    unread_count = get_unread_notifications_count()
    
    col_bell, col_mark = st.columns([1, 2])
    with col_bell:
        if st.button("🔔", key="notif_bell"):
            st.session_state.show_notifications = not st.session_state.get('show_notifications', False)
    
    if unread_count > 0:
        st.markdown(f"""
        <div style="text-align: center; margin-top: -45px; margin-left: 25px;">
            <span style="background-color: #ff4444; color: white; border-radius: 50%; 
                         padding: 2px 7px; font-size: 12px; font-weight: bold;">
                {unread_count}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_mark:
        if st.button("✓ Marquer lu", key="mark_all_read"):
            notifications = get_notifications()
            for notif in notifications:
                if not notif.get('read', False):
                    mark_notification_as_read(notif['doc_id'])
            st.rerun()
    
    # Panel de notifications
    if st.session_state.get('show_notifications', False):
        st.markdown("<div style='background-color: #2d3142; border-radius: 10px; padding: 15px; margin-top: 10px; max-height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
        notifications = get_notifications()
        
        if notifications:
            for notif in notifications:
                if notif.get('module') == 'budget' or notif.get('module') == 'general':
                    read_class = "" if notif.get('read', False) else "unread"
                    timestamp = notif.get('timestamp', 0)
                    time_ago = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
                    border_color = "#667eea" if notif.get('read', False) else "#ff4444"
                    
                    st.markdown(f"""
                    <div style='background-color: #1f2230; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid {border_color};'>
                        <div style='font-weight: bold; color: #ffffff; margin-bottom: 5px;'>{notif.get('title', 'Notification')}</div>
                        <div style='color: #a0a0a0; font-size: 14px;'>{notif.get('message', '')}</div>
                        <div style='color: #707070; font-size: 12px; margin-top: 5px;'>{time_ago}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Aucune notification")
        
        st.markdown("</div>", unsafe_allow_html=True)

with col_year:
    new_year = st.selectbox("📅 Année", options=ANNEES, index=ANNEES.index(st.session_state.selected_year), key="year_selector")
    if new_year != st.session_state.selected_year:
        st.session_state.selected_year = new_year
        save_user_preferences(st.session_state.user_profile, {
            'budget_year': new_year,
            'budget_months': st.session_state.selected_months
        })
        st.rerun()

st.divider()

# --- ONGLETS PRINCIPAUX ---
tabs = st.tabs(["📊 Tableau de Bord", "📋 Revenus", "📋 Dépenses", "📤 Importer"])

# ===== ONGLET 1: TABLEAU DE BORD =====
with tabs[0]:
    # Sélection des mois
    new_months = st.multiselect(
        "Sélectionner le(s) mois à analyser",
        options=MOIS,
        default=st.session_state.selected_months
    )
    if new_months != st.session_state.selected_months:
        st.session_state.selected_months = new_months
        save_user_preferences(st.session_state.user_profile, {
            'budget_year': st.session_state.selected_year,
            'budget_months': new_months
        })
    
    selected_months = st.session_state.selected_months
    selected_year = st.session_state.selected_year
    
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
        st.metric("📊 % Revenu Dépensé", f"{pourcentage_depense:.0f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # --- GRAPHIQUES PRINCIPAUX ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("Revenus vs Dépenses")
        if not df_expenses_filtered.empty or not df_revenues_filtered.empty:
            fig_comparison = go.Figure(data=[
                go.Bar(name='Revenus', x=['Période sélectionnée'], y=[total_revenus], 
                       marker_color='#667eea', text=[f'{total_revenus:,.0f} €'], 
                       textposition='outside'),
                go.Bar(name='Dépenses', x=['Période sélectionnée'], y=[total_depenses], 
                       marker_color='#764ba2', text=[f'{total_depenses:,.0f} €'], 
                       textposition='outside')
            ])
            fig_comparison.update_layout(
                barmode='group', 
                height=350, 
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0')
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_g2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("Répartition des Dépenses")
        if not df_expenses_filtered.empty:
            df_cat = df_expenses_filtered.groupby('Catégories')['Montant'].sum().reset_index()
            fig_pie = px.pie(df_cat, values='Montant', names='Catégories',
                            color_discrete_sequence=px.colors.sequential.Purples_r,
                            hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label+value', 
                                 texttemplate='%{label}<br>%{value:,.0f}€<br>%{percent}')
            fig_pie.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0')
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Aucune dépense enregistrée")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Graphique mensuel
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
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
    fig_monthly.add_trace(go.Bar(x=MOIS_SHORT, y=monthly_revenues, name='Revenus', 
                                 marker_color='#667eea', text=[f'{v:,.0f}€' for v in monthly_revenues],
                                 textposition='outside'))
    fig_monthly.add_trace(go.Bar(x=MOIS_SHORT, y=monthly_expenses, name='Dépenses', 
                                 marker_color='#764ba2', text=[f'{v:,.0f}€' for v in monthly_expenses],
                                 textposition='outside'))
    fig_monthly.update_layout(
        barmode='group', 
        height=400, 
        xaxis_title="Mois", 
        yaxis_title="Montant (€)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0')
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ===== ONGLET 2: REVENUS =====
with tabs[1]:
    col_header, col_button = st.columns([6, 1])
    with col_header:
        st.subheader(f"📋 Tableau des Revenus - {st.session_state.selected_year}")
    with col_button:
        st.write("")
        if st.button("➕ Ajouter", key="add_rev_btn", type="primary"):
            st.session_state.show_revenue_form = True
    
    # Pop-up pour ajouter un revenu
    if st.session_state.get('show_revenue_form', False):
        with st.form("quick_revenue_form", clear_on_submit=True):
            st.write("**💰 Ajouter un Revenu**")
            col1, col2 = st.columns(2)
            with col1:
                rev_source = st.selectbox("Source de revenu", 
                                          options=['Salaire Principal', 'Salaire Conjoint', 
                                                  'Primes', 'Revenus Complémentaires', 'Autre'],
                                          key="quick_rev_source")
                rev_amount = st.number_input("Montant (€)", min_value=0.01, step=50.0, key="quick_rev_amt")
            with col2:
                rev_month = st.selectbox("Mois", options=MOIS, key="quick_rev_month")
                rev_year = st.number_input("Année", min_value=2020, max_value=2030, value=st.session_state.selected_year, key="quick_rev_year")
            
            col_submit, col_cancel = st.columns([1, 1])
            with col_submit:
                submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
            
            if submitted:
                add_revenue(rev_source, rev_amount, rev_month, rev_year, st.session_state.user_profile)
                st.session_state.revenues = fetch_revenues()
                st.session_state.show_revenue_form = False
                st.success("✅ Revenu ajouté avec succès !")
                time.sleep(1)
                st.rerun()
            
            if cancelled:
                st.session_state.show_revenue_form = False
                st.rerun()
    
    if not df_revenues.empty and 'Année' in df_revenues.columns:
        df_rev_year = df_revenues[df_revenues['Année'] == st.session_state.selected_year].copy()
        
        if not df_rev_year.empty:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Section Modification/Suppression
            st.divider()
            st.write("**Modifier ou Supprimer un Revenu**")
            
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
                            update_expense(exp_data['doc_id'], new_cat, new_amount, new_freq, new_desc, new_month, st.session_state.selected_year, st.session_state.user_profile)
                            st.session_state.expenses = fetch_expenses()
                            st.success("✅ Dépense modifiée !")
                            time.sleep(1)
                            st.rerun()
                
                with col_del:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Supprimer", key="del_exp", type="secondary"):
                        delete_expense(exp_data['doc_id'], st.session_state.user_profile, exp_data['Catégories'], exp_data['Montant'])
                        st.session_state.expenses = fetch_expenses()
                        st.success("✅ Dépense supprimée !")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info(f"Aucune dépense enregistrée pour {st.session_state.selected_year}")
    else:
        st.info("Aucune dépense enregistrée")

# ===== ONGLET 4: IMPORT EXCEL =====
with tabs[3]:
    st.subheader("📤 Importer des données depuis Excel")
    
    col_imp1, col_imp2 = st.columns(2)
    
    with col_imp1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.write("**Format attendu pour les DÉPENSES :**")
        st.code("Catégorie | Montant | Fréquence | Mois | Année | Description")
        st.info("⚠️ IMPORTANT: La colonne doit s'appeler 'Catégorie' (sans s) et respecter exactement les noms des catégories.")
        uploaded_expenses = st.file_uploader("Importer les dépenses (.xlsx)", 
                                            type=['xlsx'], key="exp_upload")
        
        if uploaded_expenses:
            try:
                import openpyxl
                df_import_exp = pd.read_excel(uploaded_expenses)
                st.dataframe(df_import_exp.head())
                
                if st.button("Importer les dépenses", key="import_exp"):
                    imported_count = import_expenses_from_excel(df_import_exp, st.session_state.selected_year, st.session_state.user_profile)
                    st.session_state.expenses = fetch_expenses()
                    st.success(f"✅ {imported_count} dépenses importées !")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_imp2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.write("**Format attendu pour les REVENUS :**")
        st.code("Source | Montant | Mois | Année")
        uploaded_revenues = st.file_uploader("Importer les revenus (.xlsx)", 
                                            type=['xlsx'], key="rev_upload")
        
        if uploaded_revenues:
            try:
                df_import_rev = pd.read_excel(uploaded_revenues)
                st.dataframe(df_import_rev.head())
                
                if st.button("Importer les revenus", key="import_rev"):
                    imported_count = import_revenues_from_excel(df_import_rev, st.session_state.selected_year, st.session_state.user_profile)
                    st.session_state.revenues = fetch_revenues()
                    st.success(f"✅ {imported_count} revenus importés !")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 20px; color: #707070;'>
    <p>Module Budget - Famileasy v1.0.0</p>
</div>
""", unsafe_allow_html=True), 1])
                
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
                            update_revenue(rev_data['doc_id'], new_source, new_amount, new_month, st.session_state.selected_year, st.session_state.user_profile)
                            st.session_state.revenues = fetch_revenues()
                            st.success("✅ Revenu modifié !")
                            time.sleep(1)
                            st.rerun()
                
                with col_del:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Supprimer", key="del_rev", type="secondary"):
                        delete_revenue(rev_data['doc_id'], st.session_state.user_profile, rev_data['Source'], rev_data['Montant'])
                        st.session_state.revenues = fetch_revenues()
                        st.success("✅ Revenu supprimé !")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info(f"Aucun revenu enregistré pour {st.session_state.selected_year}")
    else:
        st.info("Aucun revenu enregistré")

# ===== ONGLET 3: DÉPENSES =====
with tabs[2]:
    col_header, col_button = st.columns([6, 1])
    with col_header:
        st.subheader(f"📋 Tableau des Dépenses - {st.session_state.selected_year}")
    with col_button:
        st.write("")
        if st.button("➕ Ajouter", key="add_exp_btn", type="primary"):
            st.session_state.show_expense_form = True
    
    # Pop-up pour ajouter une dépense
    if st.session_state.get('show_expense_form', False):
        with st.form("quick_expense_form", clear_on_submit=True):
            st.write("**💸 Ajouter une Dépense**")
            col1, col2 = st.columns(2)
            with col1:
                exp_category = st.selectbox("Catégorie", options=CATEGORIES_DEPENSES, key="quick_exp_cat")
                exp_amount = st.number_input("Montant (€)", min_value=0.01, step=5.0, key="quick_exp_amt")
                exp_month = st.selectbox("Mois", options=MOIS, key="quick_exp_month")
            with col2:
                exp_year = st.number_input("Année", min_value=2020, max_value=2030, value=st.session_state.selected_year, key="quick_exp_year")
                exp_frequency = st.selectbox("Fréquence", 
                                            options=['Mensuel', 'Annuel', 'Trimestriel', 
                                                    'Unique', 'Hebdomadaire'],
                                            key="quick_exp_freq")
                exp_description = st.text_input("Description (facultatif)", key="quick_exp_desc")
            
            col_submit, col_cancel = st.columns([1, 1])
            with col_submit:
                submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
            
            if submitted:
                add_expense(exp_category, exp_amount, exp_frequency, 
                           exp_description, exp_month, exp_year, st.session_state.user_profile)
                st.session_state.expenses = fetch_expenses()
                st.session_state.show_expense_form = False
                st.success("✅ Dépense ajoutée avec succès !")
                time.sleep(1)
                st.rerun()
            
            if cancelled:
                st.session_state.show_expense_form = False
                st.rerun()
    
    if not df_expenses.empty and 'Année' in df_expenses.columns:
        df_exp_year = df_expenses[df_expenses['Année'] == st.session_state.selected_year].copy()
        
        if not df_exp_year.empty:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Section Modification/Suppression
            st.divider()
            st.write("**Modifier ou Supprimer une Dépense**")
            
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
                
                col_mod, col_del = st.columns([3
