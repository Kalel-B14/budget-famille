import streamlit as st
import sys
from pathlib import Path

# Ajouter le dossier services au path
sys.path.append(str(Path(__file__).parent / "services"))

from firebase import init_firebase, get_user_profile, load_profile_image
from utils import apply_dark_theme, get_unread_notifications_count

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Famileasy - Accueil",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser Firebase
init_firebase()

# Appliquer le thème
apply_dark_theme()

# --- SÉLECTION DU PROFIL ---
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.markdown("<h1 style='text-align: center; margin-top: 100px;'>🏠 Bienvenue sur Famileasy</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0a0; margin-bottom: 50px;'>Gérez votre vie familiale en toute simplicité</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        profile_col1, profile_col2 = st.columns(2)
        
        with profile_col1:
            if st.button("👤 Margaux", use_container_width=True, key="profile_margaux"):
                st.session_state.user_profile = "Margaux"
                st.rerun()
        
        with profile_col2:
            if st.button("👤 Souliman", use_container_width=True, key="profile_souliman"):
                st.session_state.user_profile = "Souliman"
                st.rerun()
    st.stop()

# --- EN-TÊTE ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    profile_image = load_profile_image(st.session_state.user_profile)
    if profile_image:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #ffffff; margin: 0 auto 10px; 
                        overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                <img src="{profile_image}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 500;">
                Bonjour {st.session_state.user_profile}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #ffffff; margin: 0 auto 10px; 
                        display: flex; align-items: center; justify-content: center; font-size: 36px;">
                👤
            </div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 500;">
                Bonjour {st.session_state.user_profile}
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='text-align: center; margin-top: 30px;'>🏠 Famileasy</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0a0a0;'>Votre assistant familial tout-en-un</p>", unsafe_allow_html=True)

with col3:
    st.write("")
    st.write("")
    unread_count = get_unread_notifications_count()
    if unread_count > 0:
        st.info(f"🔔 {unread_count} nouvelle(s) notification(s)")

st.divider()

# --- MODULES PRINCIPAUX ---
st.markdown("<h2 style='margin-top: 30px; margin-bottom: 30px;'>📱 Vos Modules</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); padding: 30px; 
                border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                transition: transform 0.2s;'>
        <div style='font-size: 48px; margin-bottom: 15px;'>💰</div>
        <h3 style='color: #ffffff; margin-bottom: 10px;'>Budget</h3>
        <p style='color: #a0a0a0; font-size: 14px;'>Gérez vos finances familiales</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Budget", use_container_width=True, key="btn_budget"):
        st.switch_page("pages/Budget.py")

with col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); padding: 30px; 
                border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='font-size: 48px; margin-bottom: 15px;'>📅</div>
        <h3 style='color: #ffffff; margin-bottom: 10px;'>Agenda</h3>
        <p style='color: #a0a0a0; font-size: 14px;'>Organisez vos événements</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Agenda", use_container_width=True, key="btn_agenda"):
        st.switch_page("pages/Agenda.py")

with col3:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); padding: 30px; 
                border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='font-size: 48px; margin-bottom: 15px;'>🛒</div>
        <h3 style='color: #ffffff; margin-bottom: 10px;'>Courses</h3>
        <p style='color: #a0a0a0; font-size: 14px;'>Liste de courses partagée</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Courses", use_container_width=True, key="btn_courses"):
        st.switch_page("pages/Courses.py")

st.divider()

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); padding: 30px; 
                border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='font-size: 48px; margin-bottom: 15px;'>📸</div>
        <h3 style='color: #ffffff; margin-bottom: 10px;'>Galerie</h3>
        <p style='color: #a0a0a0; font-size: 14px;'>Photos et souvenirs</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Galerie", use_container_width=True, key="btn_galerie"):
        st.switch_page("pages/Galerie.py")

with col5:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); padding: 30px; 
                border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='font-size: 48px; margin-bottom: 15px;'>👤</div>
        <h3 style='color: #ffffff; margin-bottom: 10px;'>Profil</h3>
        <p style='color: #a0a0a0; font-size: 14px;'>Gérez votre profil</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Profil", use_container_width=True, key="btn_profil"):
        st.switch_page("pages/Profil.py")

with col6:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%); padding: 30px; 
                border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='font-size: 48px; margin-bottom: 15px;'>⚙️</div>
        <h3 style='color: #ffffff; margin-bottom: 10px;'>Paramètres</h3>
        <p style='color: #a0a0a0; font-size: 14px;'>Configuration</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir Paramètres", use_container_width=True, key="btn_params"):
        st.switch_page("pages/Parametres.py")

# --- STATISTIQUES RAPIDES ---
st.markdown("<h2 style='margin-top: 50px; margin-bottom: 30px;'>📊 Vue d'ensemble</h2>", unsafe_allow_html=True)

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; 
                border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='color: #ffffff; font-size: 14px; margin-bottom: 5px;'>Budget du mois</div>
        <div style='color: #ffffff; font-size: 28px; font-weight: bold;'>2 450 €</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; 
                border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='color: #ffffff; font-size: 14px; margin-bottom: 5px;'>Événements à venir</div>
        <div style='color: #ffffff; font-size: 28px; font-weight: bold;'>5</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; 
                border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='color: #ffffff; font-size: 14px; margin-bottom: 5px;'>Articles courses</div>
        <div style='color: #ffffff; font-size: 28px; font-weight: bold;'>12</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat4:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; 
                border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
        <div style='color: #ffffff; font-size: 14px; margin-bottom: 5px;'>Photos</div>
        <div style='color: #ffffff; font-size: 28px; font-weight: bold;'>247</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
