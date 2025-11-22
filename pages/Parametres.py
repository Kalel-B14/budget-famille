import streamlit as st
import sys
from pathlib import Path
from firebase_admin import firestore

# Ajouter le dossier services au path
current_dir = Path(__file__).parent.parent
services_dir = current_dir / "services"
sys.path.insert(0, str(services_dir))

# Imports des services
try:
    from firebase import init_firebase
    from utils import check_user_authentication
    from theme_manager import (
        apply_global_theme, 
        get_theme_colors, 
        COULEURS_DISPONIBLES,
        save_user_theme_preferences
    )
    SERVICES_OK = True
except ImportError as e:
    st.error(f"⚠️ Erreur d'import: {str(e)}")
    SERVICES_OK = False

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Paramètres - Famileasy",
    page_icon="⚙️",
    layout="wide"
)

# Initialiser Firebase et appliquer le thème
if SERVICES_OK:
    init_firebase()
    apply_global_theme()  # IMPORTANT : Appliquer le thème global
else:
    st.error("Services non disponibles")
    st.stop()

# Vérifier l'authentification
check_user_authentication()

# Récupérer les couleurs du thème
colors = get_theme_colors()

# --- EN-TÊTE ---
col_back, col_title = st.columns([1, 5])

with col_back:
    if st.button("← Retour"):
        st.switch_page("streamlit_app.py")

with col_title:
    st.title("⚙️ Paramètres")
    st.write(f"**Connecté :** {st.session_state.user_profile}")

st.divider()

# --- ONGLETS ---
tabs = st.tabs(["🎨 Apparence", "👤 Profil", "🔔 Notifications", "ℹ️ À propos"])

# ===== ONGLET 1: APPARENCE (CORRECTION 1) =====
with tabs[0]:
    st.header("🎨 Personnalisation de l'apparence")
    
    st.markdown("""
    <div style='background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 10px; margin: 20px 0;'>
        <p style='margin: 0;'>
            💡 Les modifications de thème s'appliquent <strong>immédiatement à toute l'application</strong> 
            et sont <strong>sauvegardées automatiquement</strong> dans votre profil.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌓 Mode d'affichage")
        
        # Mode clair/sombre
        current_mode = st.session_state.get('theme_mode', 'dark')
        mode_options = {
            "🌙 Mode Sombre": "dark",
            "☀️ Mode Clair": "light"
        }
        
        selected_mode_label = st.radio(
            "Choisissez votre mode",
            options=list(mode_options.keys()),
            index=0 if current_mode == "dark" else 1,
            key="theme_mode_radio"
        )
        
        new_mode = mode_options[selected_mode_label]
        
        # Appliquer immédiatement
        if new_mode != st.session_state.theme_mode:
            st.session_state.theme_mode = new_mode
            
            # Sauvegarder dans Firebase
            if save_user_theme_preferences(
                st.session_state.user_profile,
                new_mode,
                st.session_state.get('theme_color', 'Violet')
            ):
                st.success("✅ Mode d'affichage modifié")
                st.rerun()
    
    with col2:
        st.subheader("🎨 Couleur du thème")
        
        # Couleur primaire
        current_color = st.session_state.get('theme_color', 'Violet')
        
        # Afficher les couleurs disponibles avec des aperçus
        st.markdown("**Cliquez sur une couleur pour l'appliquer :**")
        
        # Créer une grille de boutons de couleur
        cols = st.columns(4)
        
        for idx, (color_name, color_values) in enumerate(COULEURS_DISPONIBLES.items()):
            with cols[idx % 4]:
                # Bouton avec aperçu de couleur
                is_selected = (color_name == current_color)
                border = "3px solid white" if is_selected else "1px solid #ccc"
                
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, {color_values["primary"]} 0%, {color_values["secondary"]} 100%);
                    padding: 20px;
                    border-radius: 10px;
                    border: {border};
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    margin: 5px 0;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: {"0 6px 12px rgba(0,0,0,0.3)" if is_selected else "0 2px 4px rgba(0,0,0,0.1)"};
                '>
                    {color_name}
                    {"<br>✓" if is_selected else ""}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Sélectionner {color_name}", key=f"color_{color_name}", use_container_width=True):
                    st.session_state.theme_color = color_name
                    
                    # Sauvegarder dans Firebase
                    if save_user_theme_preferences(
                        st.session_state.user_profile,
                        st.session_state.get('theme_mode', 'dark'),
                        color_name
                    ):
                        st.success(f"✅ Couleur changée en {color_name}")
                        st.rerun()
    
    st.divider()
    
    # Aperçu en temps réel
    st.subheader("👁️ Aperçu du thème actuel")
    
    col_preview1, col_preview2, col_preview3 = st.columns(3)
    
    with col_preview1:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3>Carte exemple</h3>
            <p>Voici comment apparaissent les cartes avec votre thème actuel.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_preview2:
        st.metric("Métrique", "1,234", "+12%")
    
    with col_preview3:
        st.button("Bouton exemple", use_container_width=True)

# ===== ONGLET 2: PROFIL (CORRECTION 3) =====
with tabs[1]:
    st.header("👤 Profil utilisateur")
    
    col_photo, col_info = st.columns([1, 2])
    
    with col_photo:
        st.subheader("Photo de profil")
        
        # Récupérer la photo actuelle
        try:
            db = firestore.client()
            profile_ref = db.collection('user_profiles').document(st.session_state.user_profile)
            profile_doc = profile_ref.get()
            
            current_image = None
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                current_image = profile_data.get('profile_image', '')
            
            # Afficher la photo actuelle
            if current_image:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <img src="data:image/png;base64,{current_image}" 
                         style='width: 150px; height: 150px; border-radius: 50%; border: 5px solid {colors["primary"]};'>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='
                    width: 150px; 
                    height: 150px; 
                    border-radius: 50%; 
                    border: 5px solid {colors["primary"]};
                    background: linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 60px;
                    color: white;
                    margin: 0 auto;
                '>
                    👤
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Upload de nouvelle photo
            uploaded_file = st.file_uploader(
                "Changer la photo",
                type=['png', 'jpg', 'jpeg'],
                key="profile_photo_upload"
            )
            
            if uploaded_file is not None:
                import base64
                from PIL import Image
                import io
                
                # Convertir en base64
                image = Image.open(uploaded_file)
                # Redimensionner
                image.thumbnail((200, 200))
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Sauvegarder dans Firebase
                profile_ref.set({
                    'profile_image': img_str,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                
                st.success("✅ Photo de profil mise à jour")
                st.rerun()
        
        except Exception as e:
            st.error(f"Erreur : {e}")
    
    with col_info:
        st.subheader("Informations")
        
        st.text_input("Nom d'utilisateur", value=st.session_state.user_profile, disabled=True)
        
        st.markdown("""
        ### Préférences sauvegardées
        
        Vos préférences sont automatiquement sauvegardées :
        - ✅ Thème (clair/sombre)
        - ✅ Couleur primaire
        - ✅ Photo de profil
        - ✅ Filtres et sélections (Budget, etc.)
        """)

# ===== ONGLET 3: NOTIFICATIONS =====
with tabs[2]:
    st.header("🔔 Notifications")
    
    st.checkbox("Activer les notifications", value=True)
    st.checkbox("Notifications pour le budget", value=True)
    st.checkbox("Notifications pour le calendrier", value=True)
    st.checkbox("Notifications pour les messages", value=True)
    
    st.divider()
    
    st.subheader("Historique des notifications")
    
    try:
        from firebase import get_notifications
        notifications = get_notifications()
        
        if notifications:
            for notif in notifications[:10]:
                if notif.get('user') == st.session_state.user_profile:
                    read = notif.get('read', False)
                    border_color = colors['primary'] if read else "#ff4444"
                    
                    st.markdown(f"""
                    <div class="notification-item {'unread' if not read else ''}" style='
                        border-left: 4px solid {border_color};
                        background: rgba(102, 126, 234, 0.1);
                        padding: 15px;
                        border-radius: 8px;
                        margin: 10px 0;
                    '>
                        <div style='font-weight: bold;'>{notif.get('title', '')}</div>
                        <div>{notif.get('message', '')}</div>
                        <div style='font-size: 12px; opacity: 0.7; margin-top: 5px;'>
                            {notif.get('module', '')} - 
                            {notif.get('timestamp', 0)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Aucune notification")
    
    except Exception as e:
        st.warning("Impossible de charger les notifications")

# ===== ONGLET 4: À PROPOS =====
with tabs[3]:
    st.header("ℹ️ À propos de Famileasy")
    
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
    '>
        <h1 style='color: white;'>🏠 Famileasy</h1>
        <h3 style='color: white;'>Application de gestion familiale</h3>
        <p>Version 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("📱 Modules disponibles")
        st.markdown("""
        - ✅ Budget familial
        - 📅 Agenda (à venir)
        - 🛒 Courses (à venir)
        - 📸 Galerie (à venir)
        - 👤 Profil
        - ⚙️ Paramètres
        """)
    
    with col_a2:
        st.subheader("🛠️ Technologies")
        st.markdown("""
        - **Frontend:** Streamlit
        - **Backend:** Python
        - **Database:** Firebase Firestore
        - **Graphiques:** Plotly
        - **Data:** Pandas
        """)
    
    st.divider()
    
    st.markdown("""
    ### 📝 Notes de version
    
    **v1.0.0** (Novembre 2024)
    - ✅ Module Budget complet
    - ✅ Système de notifications
    - ✅ Thème personnalisable
    - ✅ Multi-utilisateurs
    - ✅ Sauvegarde cloud
    
    ---
    
    Made with ❤️ for family management
    """)

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: {colors['primary']}; font-size: 14px; padding: 20px;'>
    <p>Paramètres - Famileasy v1.0.0</p>
</div>
""", unsafe_allow_html=True)