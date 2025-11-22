"""
Famileasy - Application de gestion familiale
Point d'entrée principal
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le dossier services au path
current_dir = Path(__file__).parent
services_dir = current_dir / "services"
sys.path.insert(0, str(services_dir))

# Imports avec gestion d'erreur
try:
    from firebase import init_firebase, load_profile_image
    from parametres_service import get_all_users, get_family_name, get_user_theme
    SERVICES_OK = True
except ImportError as e:
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
    
# Charger les utilisateurs et le nom de famille
if SERVICES_OK:
    users_list = get_all_users()
    family_name = get_family_name()
else:
    users_list = ['Margaux', 'Souliman']
    family_name = "Famille Duriez"

# --- STYLES CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #1a1d24;
        color: #e0e0e0;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .module-card {
        background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        cursor: pointer;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 2px solid transparent;
    }
    
    .module-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5);
        border: 2px solid #667eea;
        background: linear-gradient(135deg, #3d4152 0%, #2d3142 100%);
    }
    
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- SÉLECTION DU PROFIL ---
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-bottom: 50px;'>
            <div style='font-size: 80px; margin-bottom: 20px;'>🏠</div>
            <h1 style='color: #ffffff; font-size: 48px; margin-bottom: 10px;'>Famileasy</h1>
            <p style='color: #a0a0a0; font-size: 18px;'>Votre vie familiale simplifiée</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); 
                    padding: 40px; border-radius: 20px; text-align: center;'>
            <div style='font-size: 32px; font-weight: bold; color: #ffffff; margin-bottom: 10px;'>
                Bienvenue
            </div>
            <div style='color: #a0a0a0; margin-bottom: 30px; font-size: 16px;'>
                Choisissez votre profil pour continuer
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👤 Margaux", use_container_width=True, key="profile_margaux"):
                st.session_state.user_profile = "Margaux"
                st.rerun()
        
        with col2:
            if st.button("👤 Souliman", use_container_width=True, key="profile_souliman"):
                st.session_state.user_profile = "Souliman"
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #707070; font-size: 14px;'>
            <p>Version 1.0.0 | Fait avec ❤️ pour la famille</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# --- DASHBOARD PRINCIPAL ---
# Afficher l'image de profil de l'utilisateur connecté
user_image = load_profile_image(st.session_state.user_profile) if SERVICES_OK else None

col_avatar, col_header, col_settings = st.columns([1, 5, 1])

with col_avatar:
    if user_image:
        st.markdown(f"""
        <div style='width: 60px; height: 60px; border-radius: 50%; overflow: hidden;
                    border: 3px solid #667eea; margin: 10px auto;'>
            <img src='{user_image}' style='width: 100%; height: 100%; object-fit: cover;'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='width: 60px; height: 60px; border-radius: 50%; margin: 10px auto;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex; align-items: center; justify-content: center;
                    font-size: 30px; border: 3px solid white;'>
            👤
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align: center; font-size: 12px; color: #a0a0a0;'>{st.session_state.user_profile}</p>", unsafe_allow_html=True)

with col_header:
    st.markdown(f"""
    <div class='dashboard-header'>
        <div style='font-size: 28px; font-weight: bold; color: white; margin-bottom: 5px;'>
            {family_name} ▼
        </div>
        <div style='color: rgba(255, 255, 255, 0.9); font-size: 16px;'>
            {datetime.now().strftime("%A %d %B")} • 12°C ☀️
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_settings:
    st.write("")
    st.write("")
    if st.button("⚙️ Paramètres", key="settings_btn"):
        st.switch_page("pages/Parametres.py")

# Bannière d'activité
st.markdown("""
<div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); 
            padding: 20px; border-radius: 15px; margin-bottom: 30px; border-left: 4px solid #667eea;'>
    <p style='color: #ffffff; font-size: 18px; margin: 0;'>
        🎉 Votre famille a été active récemment
    </p>
</div>
""", unsafe_allow_html=True)

# Modules - Ligne 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div style='font-size: 48px; margin-bottom: 15px;'>📝</div>
            <div style='font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 5px;'>
                Listes
            </div>
            <div style='color: #a0a0a0; font-size: 14px;'>
                4 listes<br>37 éléments
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Listes", use_container_width=True, key="btn_listes"):
        st.info("Module en développement")

with col2:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div style='font-size: 48px; margin-bottom: 15px;'>📅</div>
            <div style='font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 5px;'>
                Calendrier
            </div>
            <div style='color: #a0a0a0; font-size: 14px;'>
                4 événements<br>cette semaine
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Calendrier", use_container_width=True, key="btn_calendar"):
        st.info("Module en développement")

st.markdown("<br>", unsafe_allow_html=True)

# Module Budget (mis en avant)
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 25px; border-radius: 20px; height: 180px;'>
    <div style='font-size: 48px; margin-bottom: 15px;'>💰</div>
    <div style='font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 5px;'>
        Budget Familial
    </div>
    <div style='color: rgba(255, 255, 255, 0.9); font-size: 14px;'>
        Gérez vos finances<br>en toute simplicité
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("📊 Ouvrir le Budget", use_container_width=True, key="btn_budget", type="primary"):
    st.switch_page("pages/budget_page.py")

# Modules supplémentaires
st.markdown("<br>", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div style='font-size: 48px; margin-bottom: 15px;'>📸</div>
            <div style='font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 5px;'>
                Galerie
            </div>
            <div style='color: #a0a0a0; font-size: 14px;'>
                78 photos<br>3 vidéos
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Galerie", use_container_width=True, key="btn_gallery"):
        st.info("Module en développement")

with col4:
    st.markdown("""
    <div class='module-card'>
        <div>
            <div style='font-size: 48px; margin-bottom: 15px;'>👨‍👩‍👧‍👦</div>
            <div style='font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 5px;'>
                Ma Famille
            </div>
            <div style='color: #a0a0a0; font-size: 14px;'>
                4 membres<br>actifs
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Gérer Famille", use_container_width=True, key="btn_family"):
        st.info("Module en développement")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: #707070; font-size: 14px; padding: 20px;'>
    <p>Famileasy v1.0.0 | Connecté en tant que <strong>{st.session_state.user_profile}</strong></p>
</div>
""", unsafe_allow_html=True)

if st.button("🚪 Changer de profil", key="logout_footer"):
    st.session_state.user_profile = None
    st.rerun()
