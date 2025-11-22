import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le dossier services au path
current_dir = Path(__file__).parent
services_dir = current_dir / "services"
sys.path.insert(0, str(services_dir))

# Imports des services
try:
    from firebase import init_firebase, get_firestore_client
    from utils import check_user_authentication
    from theme_manager import apply_global_theme, create_theme_selector, get_theme_colors
    SERVICES_OK = True
except ImportError as e:
    st.error(f"⚠️ Erreur d'import: {str(e)}")
    SERVICES_OK = False

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Famileasy - Accueil",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialiser Firebase
if SERVICES_OK:
    init_firebase()
    
    # IMPORTANT : Appliquer le thème global en premier
    apply_global_theme()
else:
    st.error("Services non disponibles")
    st.stop()

# Vérifier l'authentification
check_user_authentication()

# Récupérer les couleurs du thème
colors = get_theme_colors()

# --- HEADER AVEC PHOTO DE PROFIL ---
header_col1, header_col2 = st.columns([6, 1])

with header_col1:
    st.markdown(f"""
    <div class="header-container animate-in">
        <h1>Simplifiez votre</h1>
        <h1>vie de famille</h1>
        <p style='color: white; margin-top: 10px;'>
            Connecté : <strong>{st.session_state.user_profile}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Photo de profil cliquable
    st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
    
    # Récupérer la photo de profil depuis Firebase
    try:
        db = get_firestore_client()
        if db:
            profile_ref = db.collection('user_profiles').document(st.session_state.user_profile)
            profile_doc = profile_ref.get()
            
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                profile_image = profile_data.get('profile_image', '')
                
                if profile_image:
                    # Afficher la photo de profil
                    if st.button("👤", key="profile_btn", help="Accéder aux paramètres"):
                        st.switch_page("pages/Parametres.py")
                    
                    # Afficher l'image en dessous du bouton
                    st.markdown(f"""
                    <img src="data:image/png;base64,{profile_image}" 
                         class="profile-picture" 
                         alt="Photo de profil">
                    """, unsafe_allow_html=True)
                else:
                    # Pas de photo, juste un bouton
                    if st.button("👤", key="profile_btn_no_img", help="Accéder aux paramètres"):
                        st.switch_page("pages/Parametres.py")
            else:
                # Profil n'existe pas, créer un bouton par défaut
                if st.button("👤", key="profile_btn_default", help="Accéder aux paramètres"):
                    st.switch_page("pages/Parametres.py")
    except Exception as e:
        print(f"Erreur lors du chargement de la photo de profil: {e}")
        # Bouton par défaut en cas d'erreur
        if st.button("👤", key="profile_btn_error", help="Accéder aux paramètres"):
            st.switch_page("pages/Parametres.py")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- DROPDOWN FAMILLE ---
st.markdown("""
<div style='
    background: white;
    color: black;
    padding: 15px 20px;
    border-radius: 12px;
    margin: 20px 0;
    display: inline-block;
    font-weight: bold;
    font-size: 18px;
'>
    Notre Famille ▼
</div>
""", unsafe_allow_html=True)

st.divider()

# --- CARTE CALENDRIER DU JOUR (ENTIÈREMENT CLIQUABLE) ---
st.subheader("📅 Aujourd'hui")

# Container cliquable pour le calendrier
calendar_container = st.container()

with calendar_container:
    # Créer une carte cliquable avec du HTML/CSS
    st.markdown(f"""
    <div class="dashboard-card" onclick="window.location.href='pages/Agenda.py'" style='
        background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
        color: white;
        cursor: pointer;
    '>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>Mer. 6 Sept.</h2>
            <div style='
                background: white;
                color: {colors['primary']};
                padding: 10px 15px;
                border-radius: 10px;
                font-size: 28px;
                font-weight: bold;
            '>
                6
            </div>
        </div>
        
        <div style='border-left: 4px solid #ff6b6b; padding: 10px 15px; margin: 10px 0; background: rgba(255,255,255,0.1); border-radius: 8px;'>
            <div style='font-weight: bold; font-size: 16px;'>Cours de Natation Nina</div>
            <div style='opacity: 0.9;'>10h30 - 12h30</div>
        </div>
        
        <div style='border-left: 4px solid #9b59b6; padding: 10px 15px; margin: 10px 0; background: rgba(255,255,255,0.1); border-radius: 8px;'>
            <div style='font-weight: bold; font-size: 16px;'>Cinéma entre Filles</div>
            <div style='opacity: 0.9;'>14h30 - 16h30</div>
        </div>
        
        <div style='border-left: 4px solid #f39c12; padding: 10px 15px; margin: 10px 0; background: rgba(255,255,255,0.1); border-radius: 8px;'>
            <div style='font-weight: bold; font-size: 16px;'>Dîner chez Mamie</div>
            <div style='opacity: 0.9;'>19h30 - 21h30</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton invisible pour la navigation (backup si JS ne fonctionne pas)
    if st.button("📅 Voir le calendrier complet", key="calendar_btn", use_container_width=True):
        st.switch_page("pages/Agenda.py")

st.divider()

# --- GRILLE DE MODULES (CARTES ENTIÈREMENT CLIQUABLES) ---
st.subheader("📱 Modules")

# Créer 3 lignes de 2 cartes
col1, col2 = st.columns(2)

with col1:
    # LISTES
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Listes</h3>
                <p>4 listes</p>
                <p>37 tâches</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                📝
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="listes_btn", help="Ouvrir Listes", use_container_width=True):
        st.switch_page("pages/Courses.py")

with col2:
    # CALENDRIER
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Calendrier</h3>
                <p>3 événements</p>
                <p>aujourd'hui</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                📅
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="calendrier_btn", help="Ouvrir Calendrier", use_container_width=True):
        st.switch_page("pages/Agenda.py")

col3, col4 = st.columns(2)

with col3:
    # EMPLOI DU TEMPS
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Emploi du Temps</h3>
                <p>A venir : Maths</p>
                <p>10h00</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                🕐
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="emploi_btn", help="Ouvrir Emploi du Temps", use_container_width=True):
        st.info("Module Emploi du Temps à venir")

with col4:
    # REPAS
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Repas</h3>
                <p>Au dîner:</p>
                <p>Lasagnes de Mamie</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                🍽️
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="repas_btn", help="Ouvrir Repas", use_container_width=True):
        st.info("Module Repas à venir")

col5, col6 = st.columns(2)

with col5:
    # GALERIE
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Galerie</h3>
                <p>78 photos</p>
                <p>3 vidéos</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                📸
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="galerie_btn", help="Ouvrir Galerie", use_container_width=True):
        st.switch_page("pages/Galerie.py")

with col6:
    # MESSAGES
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Messages</h3>
                <p>4 messages</p>
                <p>non lus</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                💬
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="messages_btn", help="Ouvrir Messages", use_container_width=True):
        st.info("Module Messages à venir")

# Ajouter la carte BUDGET en plus
col7, col8 = st.columns(2)

with col7:
    # BUDGET
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Budget</h3>
                <p>Gérer vos</p>
                <p>finances</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                💰
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="budget_btn", help="Ouvrir Budget", use_container_width=True):
        st.switch_page("pages/Budget.py")

with col8:
    # PARAMÈTRES
    st.markdown(f"""
    <div class="dashboard-card">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3>Paramètres</h3>
                <p>Configuration</p>
                <p>de l'app</p>
            </div>
            <div style='
                font-size: 40px;
                color: {colors['primary']};
            '>
                ⚙️
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="parametres_btn", help="Ouvrir Paramètres", use_container_width=True):
        st.switch_page("pages/Parametres.py")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 20px;'>
        <h2 style='color: {colors['primary']};'>🏠 Famileasy</h2>
        <p>Application de gestion familiale</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélecteur de thème (CORRECTION 1)
    create_theme_selector()
    
    st.markdown("---")
    
    # Statistiques rapides
    st.subheader("📊 Statistiques")
    st.metric("Événements aujourd'hui", "3")
    st.metric("Tâches en cours", "37")
    st.metric("Messages non lus", "4")
    
    st.markdown("---")
    
    # Déconnexion
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user_profile = None
        st.session_state.authenticated = False
        st.rerun()

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: {colors['primary']}; font-size: 14px; padding: 20px;'>
    <p>Made with ❤️ for family management</p>
    <p>Famileasy v1.0.0 - {datetime.now().year}</p>
</div>
""", unsafe_allow_html=True)