import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Enum, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
import enum

# --- 1. ARCHITECTURE DES DONNÉES (TABLES DE LA BASE SQLite) ---
# Déclaration de la base (mapper les classes Python aux tables de la DB)
Base = declarative_base()

# Utilisation d'un Enum pour le type de transaction (Revenu ou Dépense)
class TypeTransaction(enum.Enum):
    REVENU = "Revenu"
    DEPENSE = "Dépense"

# 4.3 Table categories
class Categorie(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    nom = Column(String, unique=True, nullable=False)
    type_transaction = Column(Enum(TypeTransaction), nullable=False)

# 4.1 Table revenus
class Revenu(Base):
    __tablename__ = 'revenus'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    annee = Column(Integer, nullable=False)
    mois = Column(Integer, nullable=False)
    description = Column(String) # Utilise 'description' au lieu de 'type' pour plus de flexibilité
    montant = Column(Float, nullable=False)

# 4.2 Table depenses
class Depense(Base):
    __tablename__ = 'depenses'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    annee = Column(Integer, nullable=False)
    mois = Column(Integer, nullable=False)
    categorie = Column(String, nullable=False) # Lié au nom de la catégorie pour la simplicité
    description = Column(String)
    montant = Column(Float, nullable=False)


# --- 2. GESTION DE LA BASE DE DONNÉES (DB Manager) ---
# Utilisation de st.singleton pour initialiser la DB une seule fois
@st.singleton
class DatabaseManager:
    def __init__(self, db_url="sqlite:///budget_familial.db"):
        self.engine = create_engine(db_url)
        # Créer les tables si elles n'existent pas
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.initialize_categories()

    def get_session(self):
        return self.Session()

    def initialize_categories(self):
        """Initialise les catégories par défaut si la table est vide."""
        session = self.get_session()
        if session.query(Categorie).count() == 0:
            default_categories = [
                Categorie(nom='Salaire Souliman', type_transaction=TypeTransaction.REVENU),
                Categorie(nom='Salaire Margaux', type_transaction=TypeTransaction.REVENU),
                Categorie(nom='Allocations', type_transaction=TypeTransaction.REVENU),
                Categorie(nom='Loyer', type_transaction=TypeTransaction.DEPENSE),
                Categorie(nom='Courses', type_transaction=TypeTransaction.DEPENSE),
                Categorie(nom='Essence', type_transaction=TypeTransaction.DEPENSE),
                Categorie(nom='Factures Énergie', type_transaction=TypeTransaction.DEPENSE),
                Categorie(nom='Assurances', type_transaction=TypeTransaction.DEPENSE),
                Categorie(nom='Loisirs', type_transaction=TypeTransaction.DEPENSE),
            ]
            session.add_all(default_categories)
            session.commit()
            st.toast("Catégories initialisées !", icon="✅")
        session.close()

    # --- 5.2 Import des données (Simulation) ---
    def import_excel_data(self):
        """
        Simule l'importation de données depuis le fichier Budgets_Famille.xlsx.
        Ce code est une simulation et nécessite d'être adapté à la structure exacte
        des fichiers Excel que l'utilisateur pourrait fournir pour un vrai import.
        """
        st.info("Simulation d'importation des données Excel (5.2).")
        session = self.get_session()
        
        # Exemple de données formatées manuellement
        # Normalement, on lirait les feuilles Excel '2025', '2026', etc. pour extraire les transactions.
        
        # Simulation d'une dépense
        new_depense = Depense(
            date=date(2025, 1, 15),
            annee=2025,
            mois=1,
            categorie='Courses',
            description='Courses Leclerc Janvier',
            montant=400.00
        )
        
        # Simulation d'un revenu
        new_revenu = Revenu(
            date=date(2025, 1, 25),
            annee=2025,
            mois=1,
            description='Salaire Souliman',
            montant=1780.00
        )
        
        try:
            # Nettoyage pour éviter les doublons lors de la simulation de l'initialisation
            if session.query(Revenu).count() < 1 and session.query(Depense).count() < 1:
                session.add_all([new_depense, new_revenu])
                session.commit()
                st.success("Données d'exemple importées (Janvier 2025)!")
            else:
                st.info("Données d'exemple déjà présentes. Ignorer l'importation.")
        except Exception as e:
            st.error(f"Erreur lors de l'importation: {e}")
            session.rollback()
        finally:
            session.close()

    def get_all_transactions(self, annee=None):
        """Récupère toutes les transactions (revenus et dépenses) dans un DataFrame."""
        session = self.get_session()
        
        # Requête des revenus
        revenus = session.query(Revenu).all()
        df_revenus = pd.DataFrame([r.__dict__ for r in revenus])
        if '_sa_instance_state' in df_revenus.columns:
            df_revenus = df_revenus.drop(columns=['_sa_instance_state'])
        df_revenus['Type'] = 'Revenu'
        df_revenus['Catégorie'] = df_revenus['description'] # Utiliser la description comme catégorie pour les revenus

        # Requête des dépenses
        depenses = session.query(Depense).all()
        df_depenses = pd.DataFrame([d.__dict__ for d in depenses])
        if '_sa_instance_state' in df_depenses.columns:
            df_depenses = df_depenses.drop(columns=['_sa_instance_state'])
        df_depenses['Type'] = 'Dépense'

        session.close()
        
        # Renommer les colonnes pour la concaténation
        df_revenus = df_revenus[['id', 'date', 'annee', 'mois', 'Catégorie', 'montant', 'Type']]
        df_depenses = df_depenses[['id', 'date', 'annee', 'mois', 'categorie', 'montant', 'Type']].rename(columns={'categorie': 'Catégorie'})

        df_full = pd.concat([df_revenus, df_depenses], ignore_index=True)
        
        if annee is not None:
            df_full = df_full[df_full['annee'] == annee]
        
        return df_full.sort_values(by='date', ascending=False)

# Initialisation du gestionnaire de base de données
db_manager = DatabaseManager()

# --- 3. STRUCTURE FONCTIONNELLE DE L'APPLICATION (PAGES) ---

# Définition des pages
PAGES = {
    "📊 Tableau de Bord": "dashboard",
    "➕ Saisie de Transaction": "saisie",
    "⚙️ Gestion des Catégories": "categories"
}

# 6.2 Page Saisie
def page_saisie():
    st.header("➕ Saisie d'une Nouvelle Transaction")
    
    session = db_manager.get_session()
    categories_obj = session.query(Categorie).all()
    session.close()
    
    # Séparer les catégories pour les Revenus et Dépenses
    cat_revenus = [c.nom for c in categories_obj if c.type_transaction == TypeTransaction.REVENU]
    cat_depenses = [c.nom for c in categories_obj if c.type_transaction == TypeTransaction.DEPENSE]
    
    # Formulaire principal
    with st.form("formulaire_transaction", clear_on_submit=True):
        st.subheader("Informations de la transaction")
        
        # 3.2.1/3.2.2 - Choix du type (Revenu ou Dépense)
        type_saisi = st.radio(
            "Type de transaction",
            ('Dépense', 'Revenu'),
            index=0,
            horizontal=True
        )

        col_date, col_montant = st.columns(2)
        date_saisie = col_date.date_input("Date de la transaction", datetime.now())
        montant_saisie = col_montant.number_input("Montant", min_value=0.01, format="%.2f")
        
        # Choix de la catégorie dynamique
        if type_saisi == 'Revenu':
            categorie_saisie = st.selectbox("Catégorie / Source du revenu", cat_revenus)
        else:
            categorie_saisie = st.selectbox("Catégorie de dépense", cat_depenses)

        description_saisie = st.text_input("Description (ex: Courses Leclerc)", max_chars=255)

        submitted = st.form_submit_button("Enregistrer la transaction")

        if submitted:
            # 7. Validation des saisies
            if montant_saisie <= 0:
                st.error("Le montant doit être supérieur à zéro.")
                return

            annee = date_saisie.year
            mois = date_saisie.month
            
            new_session = db_manager.get_session()
            
            try:
                if type_saisi == 'Revenu':
                    new_entry = Revenu(
                        date=date_saisie,
                        annee=annee,
                        mois=mois,
                        description=categorie_saisie, # Pour les revenus, on utilise la catégorie comme description
                        montant=montant_saisie
                    )
                    new_session.add(new_entry)
                else: # Dépense
                    new_entry = Depense(
                        date=date_saisie,
                        annee=annee,
                        mois=mois,
                        categorie=categorie_saisie,
                        description=description_saisie,
                        montant=montant_saisie
                    )
                    new_session.add(new_entry)
                
                new_session.commit()
                st.success(f"✅ Transaction ({type_saisi}) enregistrée avec succès dans la base de données!")
                # Recharger les données après l'ajout
                st.session_state.data_update_trigger = True
                
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement : {e}")
                new_session.rollback()
            finally:
                new_session.close()

# 6.3 Page Catégories
def page_categories():
    st.header("⚙️ Gestion des Catégories et Typologies")
    
    session = db_manager.get_session()
    categories_obj = session.query(Categorie).all()
    
    # Convertir en DataFrame pour l'affichage et la modification
    df_categories = pd.DataFrame([
        {'id': c.id, 'Nom': c.nom, 'Type': c.type_transaction.value} 
        for c in categories_obj
    ]).sort_values(by=['Type', 'Nom'])
    
    st.subheader("Catégories Actuelles")
    # Affichage de la liste des catégories
    st.dataframe(df_categories, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Ajouter une nouvelle Typologie")

    with st.form("formulaire_categorie", clear_on_submit=True):
        nom_saisi = st.text_input("Nom de la nouvelle catégorie (ex: Alimentation - Bio)")
        type_saisi = st.selectbox("Type", ('Dépense', 'Revenu'))
        
        submitted = st.form_submit_button("Ajouter la Catégorie")
        
        if submitted:
            if not nom_saisi:
                st.error("Veuillez entrer un nom pour la catégorie.")
            elif nom_saisi in df_categories['Nom'].tolist():
                st.error("Cette catégorie existe déjà.")
            else:
                try:
                    new_type = TypeTransaction.REVENU if type_saisi == 'Revenu' else TypeTransaction.DEPENSE
                    new_categorie = Categorie(nom=nom_saisi, type_transaction=new_type)
                    session.add(new_categorie)
                    session.commit()
                    st.success(f"Catégorie '{nom_saisi}' ({type_saisi}) ajoutée !")
                    st.rerun() # Rafraîchir la page
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout: {e}")
                    session.rollback()
    
    session.close()


# 6.1 Page Tableau de Bord
@st.cache_data(ttl=60) # Mise en cache des données pour améliorer les performances (Interface réactive 7.)
def get_dashboard_data(db_manager, annee_selectionnee):
    """Récupère et agrège les données pour le tableau de bord."""
    df = db_manager.get_all_transactions(annee=annee_selectionnee)
    
    # Agrégation des totaux mensuels
    df_mensuel = df.groupby(['annee', 'mois', 'Type'])['montant'].sum().unstack(fill_value=0).reset_index()
    df_mensuel['Solde'] = df_mensuel.get('Revenu', 0) - df_mensuel.get('Dépense', 0)
    
    # Agrégation des dépenses par catégorie
    df_dep_categories = df[df['Type'] == 'Dépense'].groupby('Catégorie')['montant'].sum().reset_index()
    
    return df, df_mensuel, df_dep_categories

def page_dashboard():
    st.header("📊 Tableau de Bord Financier")
    
    # 3.2.4 Gestion multi-annuelle : Récupérer toutes les années disponibles
    all_transactions = db_manager.get_all_transactions()
    available_years = sorted(all_transactions['annee'].unique().tolist(), reverse=True)
    current_year = datetime.now().year
    
    # Si aucune année n'est disponible, utiliser l'année courante
    if not available_years:
        available_years = [current_year]

    # Sélecteur d'année (3.1)
    if 'selected_year' not in st.session_state or st.session_state.selected_year not in available_years:
        st.session_state.selected_year = available_years[0]
        
    st.session_state.selected_year = st.selectbox(
        "Sélectionnez l'année", 
        available_years,
        index=available_years.index(st.session_state.selected_year)
    )
    
    # Récupérer les données mises en cache pour l'année sélectionnée
    df_full, df_mensuel, df_dep_categories = get_dashboard_data(db_manager, st.session_state.selected_year)

    # 3.1 Vue globale du budget actuel
    total_revenus = df_full[df_full['Type'] == 'Revenu']['montant'].sum()
    total_depenses = df_full[df_full['Type'] == 'Dépense']['montant'].sum()
    solde = total_revenus - total_depenses
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric(f"💰 Total Revenus {st.session_state.selected_year}", f"{total_revenus:,.0f} €")
    col2.metric(f"💸 Total Dépenses {st.session_state.selected_year}", f"{total_depenses:,.0f} €")
    col3.metric(f"✨ Solde {st.session_state.selected_year}", f"{solde:,.0f} €", delta=f"{solde:,.0f} €")
    st.markdown("---")

    # --- Graphiques interactifs (3.1 & 5.1) ---
    
    # Évolution du solde mensuel (courbe)
    st.subheader(f"Évolution Mensuelle du Solde et des Flux ({st.session_state.selected_year})")
    
    # Remplacement des numéros de mois par les noms pour le graphique
    mois_map = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin', 7: 'Juil', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
    df_mensuel['Mois_Nom'] = df_mensuel['mois'].map(mois_map)

    # Graphique en barres pour Revenus/Dépenses et ligne pour le Solde
    fig_flow = px.bar(
        df_mensuel.sort_values(by='mois'), 
        x='Mois_Nom', 
        y=['Revenu', 'Dépense'],
        title='Flux Mensuels (Revenus vs Dépenses)',
        barmode='group',
        color_discrete_map={'Revenu': '#2ecc71', 'Dépense': '#e74c3c'}
    )
    
    fig_solde_line = px.line(
        df_mensuel.sort_values(by='mois'), 
        x='Mois_Nom', 
        y='Solde', 
        markers=True,
        line_shape='spline'
    )
    # Ajouter la ligne de solde sur le graphique des flux
    fig_flow.add_trace(fig_solde_line.data[0].update(
        yaxis='y2', name='Solde', line=dict(color='#3498db', width=4)
    ))

    # Configuration du double axe Y
    fig_flow.update_layout(
        yaxis=dict(title='Montant Flux (€)'),
        yaxis2=dict(title='Solde (€)', overlaying='y', side='right', showgrid=False)
    )
    
    st.plotly_chart(fig_flow, use_container_width=True)


    # Répartition des dépenses par catégories (Pie / Donut)
    col_pie, col_transac = st.columns([1, 2])
    
    with col_pie:
        st.subheader("Répartition des Dépenses")
        if not df_dep_categories.empty:
            fig_pie = px.pie(
                df_dep_categories, 
                values='montant', 
                names='Catégorie', 
                hole=0.4, 
                title=f"Total: {total_depenses:,.0f} €"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Pas de dépenses enregistrées pour cette année.")

    # 5.1 Filtrage dynamique & 6.1 Dernières transactions
    with col_transac:
        st.subheader("Détail des Transactions")
        st.dataframe(
            df_full[['date', 'Type', 'Catégorie', 'montant', 'description']].rename(columns={
                'date': 'Date', 'montant': 'Montant (€)', 'description': 'Description'
            }),
            use_container_width=True,
            hide_index=True
        )


# --- LOGIQUE PRINCIPALE DE L'APPLICATION ---

def main():
    st.sidebar.title("Navigation")
    
    # 5.4 Sauvegarde automatique / Import initial
    db_manager.import_excel_data() # Tente d'importer les données d'exemple

    # Logique pour la navigation (Sidebar)
    page_name = st.sidebar.radio("Aller à la page", list(PAGES.keys()))
    
    if page_name == "📊 Tableau de Bord":
        page_dashboard()
    elif page_name == "➕ Saisie de Transaction":
        page_saisie()
    elif page_name == "⚙️ Gestion des Catégories":
        page_categories()
        
    # Section footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Architecturé pour le Cahier des Charges - Base SQLite (Local/Cloud)")


if __name__ == "__main__":
    main()
