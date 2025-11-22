import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import base64

# Ajouter le dossier services au path
sys.path.append(str(Path(__file__).parent / "services"))

from firebase import init_firebase, load_profile_image, get_unread_notifications_count
from utils import apply_dark_theme

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Famileasy - Accueil",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialiser Firebase
init_firebase()

# Appliquer le thème
apply_dark_theme()

# --- STYLES ADDITIONNELS ---
st.markdown("""
<style>
    /* Login Card */
    .login-card {
        background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        text-align: center;
        max-width: 400px;
        margin: 0 auto;
    }
    
    .login-title {
        font-size: 32px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    
    .login-subtitle {
        color: #a0a0a0;
        margin-bottom: 30px;
        font-size: 16px;
    }
    
    /* Profile Selection */
    .profile-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 15px;
        border: none;
        font-size: 18px;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .profile-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Dashboard Header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="15" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="80" r="20" fill="rgba(255,255,255,0.1)"/></svg>');
        opacity: 0.3;
    }
    
    .family-name {
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin-bottom: 5px;
    }
    
    .date-weather {
        color: rgba(255, 255, 255, 0.9);
        font-size: 16px;
    }
    
    /* Module Cards */
    .module-card {
        background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
    }
    
    .module-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    .module-title {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 5px;
    }
    
    .module-subtitle {
        color: #a0a0a0;
        font-size: 14px;
    }
    
    .module-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background: #ff4444;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Activity Banner */
    .activity-banner {
        background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        border-left: 4px solid #667eea;
    }
    
    .activity-text {
        color: #ffffff;
        font-size: 18px;
        margin: 0;
    }
    
    /* User Avatar */
    .user-avatar-small {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        overflow: hidden;
        border: 3px solid white;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .user-avatar-small img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

# --- SÉLECTION DU PROFIL (PAGE DE CONNEXION) ---
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    # Logo et titre centré
    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Logo Famileasy
        st.markdown("""
        <div style='text-align: center; margin-bottom: 50px;'>
            <div style='font-size: 80px; margin-bottom: 20px;'>🏠</div>
            <h1 style='color: #ffffff; font-size: 48px; margin-bottom: 10px;'>Famileasy</h1>
            <p style='color: #a0a0a0; font-size: 18px;'>Votre vie familiale simplifiée</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card de connexion
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<div class='login-title'>Bienvenue</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-subtitle'>Choisissez votre profil pour continuer</div>", unsafe_allow_html=True)
        
        # Boutons de sélection de profil
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👤 Margaux", use_container_width=True, key="profile_margaux"):
                st.session_state.user_profile = "Margaux"
                st.rerun()
        
        with col2:
            if st.button("👤 Souliman", use_container_width=True, key="profile_souliman"):
                st.session_state.user_profile = "Souliman"
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #707070; font-size: 14px;'>
            <p>Version 1.0.0 | Fait avec ❤️ pour la famille</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# --- DASHBOARD PRINCIPAL ---

# En-tête avec profil et paramètres
col_avatar, col_family, col_settings = st.columns([1, 6, 1])

with col_avatar:
    profile_image = load_profile_image(st.session_state.user_profile)
    if profile_image:
        st.markdown(f"""
        <div class='user-avatar-small'>
            <img src="{profile_image}" alt="Profile">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex; align-items: center; justify-content: center; font-size: 24px; border: 3px solid white;'>
            👤
        </div>
        """, unsafe_allow_html=True)

with col_family:
    current_date = datetime.now().strftime("%A %d %B")
    st.markdown(f"""
    <div class='dashboard-header'>
        <div class='family-name'>Famille Martin ▼</div>
        <div class='date-weather'>{current_date} • 12°C ☀️</div>
    </div>
    """, unsafe_allow_html=True)

with col_settings:
    if st.button("⚙️", key="settings_btn"):
        st.switch_page("pages/Parametres.py")

# Bannière d'activité
st.markdown("""
<div class='activity-banner'>
    <p class='activity-text'>🎉 Votre famille a été active récemment</p>
    <button style='background: rgba(102, 126, 234, 0.2); color: white; border: none; padding: 8px 16px; 
                   border-radius: 8px; cursor: pointer; margin-top: 10px;'>
        ⚙️ Voir les dernières actualités →
    </button>
</div>
""", unsafe_allow_html=True)

# Modules - Ligne 1
col1, col2 = st.columns(2)

with col1:
    unread_courses = 12  # À remplacer par vraie donnée
    st.markdown(f"""
    <div class='module-card'>
        <div>
            <div class='module-icon'>📝</div>
            <div class='module-title'>Listes</div>
            <div class='module-subtitle'>4 listes<br>37 éléments</div>
        </div>
        {f"<div class='module-badge'>{unread_courses}</div>" if unread_courses > 0 else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Listes", use_container_width=True, key="btn_listes"):
        st.switch_page("pages/Courses.py")

with col2:
    events_count = 4  # À remplacer par vraie donnée
    st.markdown(f"""
    <div class='module-card'>
        <div>
            <div class='module-icon'>📅</div>
            <div class='module-title'>Calendrier</div>
            <div class='module-subtitle'>{events_count} événements<br>cette semaine</div>
        </div>
        {f"<div class='module-badge'>{events_count}</div>" if events_count > 0 else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Calendrier", use_container_width=True, key="btn_calendar"):
        st.switch_page("pages/Agenda.py")

st.markdown("<br>", unsafe_allow_html=True)

# Modules - Ligne 2
col3, col4 = st.columns(2)

with col3:
    meals_today = 2  # À remplacer par vraie donnée
    st.markdown(f"""
    <div class='module-card'>
        <div>
            <div class='module-icon'>🍽️</div>
            <div class='module-title'>Repas</div>
            <div class='module-subtitle'>{meals_today} repas prévus<br>aujourd'hui</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Voir les Repas", use_container_width=True, key="btn_meals"):
        st.info("Module Repas - En développement")

with col4:
    unread_messages = 4  # À remplacer par vraie donnée
    st.markdown(f"""
    <div class='module-card'>
        <div>
            <div class='module-icon'>💬</div>
            <div class='module-title'>Messages</div>
            <div class='module-subtitle'>{unread_messages} messages<br>non lus</div>
        </div>
        {f"<div class='module-badge'>{unread_messages}</div>" if unread_messages > 0 else ""}
    </div>
    """, unsafe_allow_html=True)
    if st.button("Voir Messages", use_container_width=True, key="btn_messages"):
        st.info("Module Messages - En développement")

st.markdown("<br>", unsafe_allow_html=True)

# Modules - Ligne 3
col5, col6 = st.columns(2)

with col5:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div class='module-icon'>📍</div>
            <div class='module-title'>Localisation</div>
            <div class='module-subtitle'>3 places<br>enregistrées</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Voir Localisation", use_container_width=True, key="btn_location"):
        st.info("Module Localisation - En développement")

with col6:
    photos_count = 78  # À remplacer par vraie donnée
    st.markdown(f"""
    <div class='module-card'>
        <div>
            <div class='module-icon'>📸</div>
            <div class='module-title'>Galerie</div>
            <div class='module-subtitle'>{photos_count} photos<br>3 vidéos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Galerie", use_container_width=True, key="btn_gallery"):
        st.switch_page("pages/Galerie.py")

st.markdown("<br>", unsafe_allow_html=True)

# Modules - Ligne 4
col7, col8 = st.columns(2)

with col7:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div class='module-icon'>👥</div>
            <div class='module-title'>Contacts</div>
            <div class='module-subtitle'>16 contacts<br>enregistrés</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Voir Contacts", use_container_width=True, key="btn_contacts"):
        st.info("Module Contacts - En développement")

with col8:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div class='module-icon'>👨‍👩‍👧‍👦</div>
            <div class='module-title'>Ma Famille</div>
            <div class='module-subtitle'>4 membres<br>actifs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Gérer Famille", use_container_width=True, key="btn_family"):
        st.switch_page("pages/Profil.py")

st.markdown("<br>", unsafe_allow_html=True)

# Module Budget (mis en avant)
st.markdown("""
<div class='module-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
    <div>
        <div class='module-icon'>💰</div>
        <div class='module-title'>Budget Familial</div>
        <div class='module-subtitle'>Gérez vos finances<br>en toute simplicité</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("📊 Ouvrir le Budget", use_container_width=True, key="btn_budget", type="primary"):
    st.switch_page("pages/Budget.py")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #707070; font-size: 14px; padding: 20px;'>
    <p>Famileasy v1.0.0 | Connecté en tant que <strong>{}</strong></p>
    <button style='background: transparent; color: #667eea; border: 1px solid #667eea; padding: 8px 16px; 
                   border-radius: 8px; cursor: pointer; margin-top: 10px;'>
        🚪 Changer de profil
    </button>
</div>
""".format(st.session_state.user_profile), unsafe_allow_html=True)

if st.button("Changer de profil", key="logout_footer"):
    st.session_state.user_profile = None
    st.rerun()
