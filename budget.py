import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Budget Famille 2025", layout="wide")

st.title("🏠 Gestion Budget Famille - 2025")

# --- DONNÉES (SIMULATION BASÉE SUR VOTRE CSV) ---
# Dans une version finale, on chargerait directement votre CSV.
# Ici, je recrée la structure pour que l'appli fonctionne tout de suite.

mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

# Structure des données de revenus (basé sur votre fichier)
data_revenus = {
    "Mois": mois,
    "Souliman": [1780]*11 + [1940],
    "Margaux": [1650]*8 + [1665, 1700, 1650, 1650],
    "Impôt (Remboursement)": [0,0,0,0,600,0,0,0,0,0,0,0],
    "Primes/Divers": [250,0,0,0,2500,800,0,0,140,70,140,1240]
}
df_revenus = pd.DataFrame(data_revenus)
df_revenus['Total Revenus'] = df_revenus.select_dtypes(include='number').sum(axis=1)

# Structure des données de dépenses (Principaux postes extraits de votre fichier)
data_depenses = {
    "Mois": mois,
    "Loyer": [792]*12,
    "Crédit Voiture": [292]*12,
    "Courses": [400]*11 + [470],
    "Ecole Clémence": [350]*8 + [70, 260, 450, 36],
    "Essence": [100,100,100,100,100,100,100,150,100,100,100,80],
    "Factures (Energie/Eau/Internet/Tel)": [170+47+45+33]*12, # Simplifié pour l'exemple
    "Loisirs & Cadeaux": [140, 150, 0, 150, 20, 70, 0, 140, 120, 0, 340, 440],
    "Frais Bancaires/Découvert": [0,0,0,0,0,0,0,815,400,1200,527,0]
}
df_depenses = pd.DataFrame(data_depenses)
df_depenses['Total Dépenses'] = df_depenses.select_dtypes(include='number').sum(axis=1)

# Calcul du Solde
df_global = pd.DataFrame({
    "Mois": mois,
    "Revenus": df_revenus['Total Revenus'],
    "Dépenses": df_depenses['Total Dépenses']
})
df_global['Solde'] = df_global['Revenus'] - df_global['Dépenses']
df_global['Cumul Annuel'] = df_global['Solde'].cumsum()

# --- SIDEBAR (Barre latérale) ---
st.sidebar.header("Filtres & Options")
mois_selectionne = st.sidebar.selectbox("Sélectionner un mois pour le détail", mois)

# --- INDICATEURS CLÉS (KPI) ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

total_rev_annuel = df_revenus['Total Revenus'].sum()
total_dep_annuel = df_depenses['Total Dépenses'].sum()
epargne_theorique = total_rev_annuel - total_dep_annuel

col1.metric("💰 Revenus Annuels 2025", f"{total_rev_annuel:,.0f} €")
col2.metric("💸 Dépenses Annuelles 2025", f"{total_dep_annuel:,.0f} €", delta_color="inverse")
col3.metric("🐷 Reste à vivre / Épargne", f"{epargne_theorique:,.0f} €", delta=f"{(epargne_theorique/total_rev_annuel)*100:.1f}% du revenu")

st.markdown("---")

# --- GRAPHIQUES ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Évolution Mensuelle : Revenus vs Dépenses")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_global['Mois'], y=df_global['Revenus'], name='Revenus', marker_color='#2ecc71'))
    fig.add_trace(go.Bar(x=df_global['Mois'], y=df_global['Dépenses'], name='Dépenses', marker_color='#e74c3c'))
    
    # Ligne de solde
    fig.add_trace(go.Scatter(x=df_global['Mois'], y=df_global['Solde'], name='Solde du mois', line=dict(color='blue', width=2)))
    
    fig.update_layout(barmode='group', height=400)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Répartition des Dépenses (Annuel)")
    # On transpose pour avoir les catégories
    depenses_categories = df_depenses.drop(columns=['Mois', 'Total Dépenses']).sum().reset_index()
    depenses_categories.columns = ['Catégorie', 'Montant']
    
    fig_pie = px.pie(depenses_categories, values='Montant', names='Catégorie', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TABLEAU DÉTAILLÉ ÉDITABLE ---
st.subheader(f"Détail pour {mois_selectionne}")

# On récupère les données du mois sélectionné
idx = mois.index(mois_selectionne)
detail_rev = df_revenus.iloc[idx].drop('Total Revenus').to_dict()
detail_dep = df_depenses.iloc[idx].drop('Total Dépenses').to_dict()

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.info("📥 Entrées")
    st.table(pd.DataFrame(list(detail_rev.items()), columns=['Source', 'Montant']))

with col_d2:
    st.warning("📤 Sorties")
    st.table(pd.DataFrame(list(detail_dep.items()), columns=['Poste', 'Montant']))

# --- SECTION MODIFICATION ---
st.markdown("---")
st.caption("Cette application est une démo basée sur votre fichier CSV. Pour l'utiliser réellement, nous connecterions ce code directement à votre fichier 'Budgets_Famille.xlsx'.")