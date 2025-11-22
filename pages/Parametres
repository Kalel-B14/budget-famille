import streamlit as st
import sys
from pathlib import Path
import base64
import time

# Ajouter le dossier services au path
current_dir = Path(__file__).parent.parent
services_dir = current_dir / "services"
sys.path.insert(0, str(services_dir))

# Imports des services
try:
    from firebase import (init_firebase, save_profile_image, load_profile_image,
                         save_user_preferences, load_user_preferences, get_db)
    from parametres_service import (get_all_users, add_user, delete_user,
                                   get_family_name, set_family_name,
                                   get_expense_categories, add_expense_category, delete_expense_category,
                                   get_revenue_sources, add_revenue_source, delete_revenue_source,
                                   get_user_theme, save_user_theme)
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

# Vérifier l'authentification
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.error("⚠️ Veuillez vous connecter")
    if st.button("Retour à l'accueil"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Initialiser Firebase
if SERVICES_OK:
    init_firebase()

# --- PALETTES DE COULEURS ---
PALETTES = {
    'Violet': {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent': '#8b5cf6',
        'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    'Bleu': {
        'primary': '#4299e1',
        'secondary': '#3182ce',
        'accent': '#2b6cb0',
        'gradient': 'linear-gradient(135deg, #4299e1 0%, #3182ce 100%)'
    },
    'Vert': {
        'primary': '#48bb78',
        'secondary': '#38a169',
        'accent': '#2f855a',
        'gradient': 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)'
    },
    'Rose': {
        'primary': '#ed64a6',
        'secondary': '#d53f8c',
        'accent': '#b83280',
        'gradient': 'linear-gradient(135deg, #ed64a6 0%, #d53f8c 100%)'
    },
    'Rouge': {
        'primary': '#f56565',
        'secondary': '#e53e3e',
        'accent': '#c53030',
        'gradient': 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)'
    }
}

# Charger le thème utilisateur
if SERVICES_OK:
    user_theme = get_user_theme(st.session_state.user_profile)
    theme_mode = user_theme.get('mode', 'dark') if user_theme else 'dark'
    theme_palette = user_theme.get('palette', 'Violet') if user_theme else 'Violet'
else:
    theme_mode = 'dark'
    theme_palette = 'Violet'

palette = PALETTES[theme_palette]

# Appliquer les styles dynamiques
bg_color = '#1a1d24' if theme_mode == 'dark' else '#f7fafc'
text_color = '#e0e0e0' if theme_mode == 'dark' else '#2d3748'
card_bg = 'linear-gradient(135deg, #2d3142 0%, #1f2230 100%)' if theme_mode == 'dark' else 'linear-gradient(135deg, #ffffff 0%, #f7fafc 100%)'

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    h1, h2, h3 {{
        color: {text_color} !important;
    }}
    
    .metric-card {{
        background: {card_bg};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }}
    
    .stButton > button {{
        background: {palette['gradient']};
        color: white;
        border-radius: 10px;
        border: none;
    }}
    
    .stButton > button:hover {{
        opacity: 0.9;
        box-shadow: 0 4px 12px {palette['primary']}40;
    }}
    
    .color-preview {{
        width: 100%;
        height: 60px;
        border-radius: 10px;
        background: {palette['gradient']};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin: 10px 0;
    }}
</style>
""", unsafe_allow_html=True)

# --- EN-TÊTE ---
col_back, col_title = st.columns([1, 5])

with col_back:
    if st.button("← Retour"):
        st.switch_page("streamlit_app.py")

with col_title:
    st.title("⚙️ Paramètres")
    st.write(f"**Utilisateur:** {st.session_state.user_profile}")

st.divider()

# --- ONGLETS ---
tabs = st.tabs(["👤 Profil", "👥 Utilisateurs", "🏠 Famille", "💰 Budget", "🎨 Thème"])

# ===== ONGLET 1: PROFIL =====
with tabs[0]:
    st.subheader("👤 Mon Profil")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Affichage photo actuelle
        st.write("**Photo de profil actuelle**")
        current_image = load_profile_image(st.session_state.user_profile) if SERVICES_OK else None
        
        if current_image:
            st.markdown(f"""
            <div style='width: 150px; height: 150px; border-radius: 50%; overflow: hidden; 
                        border: 4px solid {palette['primary']}; margin: 20px auto;'>
                <img src="{current_image}" style='width: 100%; height: 100%; object-fit: cover;'>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='width: 150px; height: 150px; border-radius: 50%; 
                        background: {palette['gradient']}; margin: 20px auto;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 60px; border: 4px solid {palette['primary']};'>
                👤
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.write("**Modifier la photo de profil**")
        uploaded_file = st.file_uploader(
            "Choisir une nouvelle photo",
            type=['png', 'jpg', 'jpeg'],
            key="profile_upload",
            help="Format accepté: PNG, JPG, JPEG (max 5MB)"
        )
        
        if uploaded_file:
            # Prévisualisation
            st.write("**Prévisualisation:**")
            st.image(uploaded_file, width=150)
            
            if st.button("💾 Enregistrer cette photo", type="primary"):
                if SERVICES_OK:
                    try:
                        bytes_data = uploaded_file.read()
                        base64_image = base64.b64encode(bytes_data).decode()
                        image_data = f"data:image/{uploaded_file.type.split('/')[1]};base64,{base64_image}"
                        
                        save_profile_image(st.session_state.user_profile, image_data)
                        st.success("✅ Photo de profil mise à jour !")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
                else:
                    st.warning("Firebase non disponible")

# ===== ONGLET 2: UTILISATEURS =====
with tabs[1]:
    st.subheader("👥 Gestion des Utilisateurs")
    
    if SERVICES_OK:
        users = get_all_users()
        
        # Affichage des utilisateurs existants
        st.write("**Utilisateurs actuels:**")
        
        cols = st.columns(min(len(users), 4))
        for idx, user in enumerate(users):
            with cols[idx % 4]:
                user_image = load_profile_image(user)
                
                st.markdown(f"""
                <div class='metric-card' style='text-align: center;'>
                    <div style='width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 10px;
                                background: {palette['gradient']}; overflow: hidden;
                                border: 3px solid {palette['primary']};'>
                        {"<img src='" + user_image + "' style='width: 100%; height: 100%; object-fit: cover;'>" if user_image else "<div style='font-size: 40px; padding-top: 20px;'>👤</div>"}
                    </div>
                    <div style='font-weight: bold; margin-bottom: 10px;'>{user}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if len(users) > 2 and user != st.session_state.user_profile:
                    if st.button(f"🗑️ Supprimer", key=f"del_user_{user}"):
                        if delete_user(user):
                            st.success(f"✅ {user} supprimé")
                            time.sleep(1)
                            st.rerun()
        
        st.divider()
        
        # Ajouter un utilisateur
        st.write("**Ajouter un nouvel utilisateur:**")
        
        with st.form("add_user_form"):
            new_user_name = st.text_input(
                "Nom du nouvel utilisateur",
                placeholder="Ex: Papa, Maman, Enfant..."
            )
            
            if st.form_submit_button("➕ Ajouter l'utilisateur"):
                if new_user_name and new_user_name not in users:
                    if add_user(new_user_name):
                        st.success(f"✅ {new_user_name} ajouté avec succès !")
                        time.sleep(1)
                        st.rerun()
                elif new_user_name in users:
                    st.error("❌ Cet utilisateur existe déjà")
                else:
                    st.error("❌ Veuillez entrer un nom")
    else:
        st.warning("Firebase non disponible")

# ===== ONGLET 3: FAMILLE =====
with tabs[2]:
    st.subheader("🏠 Paramètres Famille")
    
    if SERVICES_OK:
        current_family_name = get_family_name()
        
        st.write("**Nom de famille affiché sur la page d'accueil**")
        
        with st.form("family_name_form"):
            new_family_name = st.text_input(
                "Nom de famille",
                value=current_family_name,
                placeholder="Ex: Famille Dupont"
            )
            
            if st.form_submit_button("💾 Enregistrer"):
                if new_family_name:
                    if set_family_name(new_family_name):
                        st.success("✅ Nom de famille mis à jour !")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("❌ Le nom ne peut pas être vide")
    else:
        st.warning("Firebase non disponible")

# ===== ONGLET 4: BUDGET =====
with tabs[3]:
    st.subheader("💰 Paramètres Budget")
    
    col_cat, col_rev = st.columns(2)
    
    # Catégories de dépenses
    with col_cat:
        st.write("**📝 Catégories de Dépenses**")
        
        if SERVICES_OK:
            categories = get_expense_categories()
            
            # Afficher les catégories
            for cat in categories:
                col_name, col_action = st.columns([4, 1])
                with col_name:
                    st.text(f"• {cat}")
                with col_action:
                    if st.button("🗑️", key=f"del_cat_{cat}"):
                        if delete_expense_category(cat):
                            st.success("✅ Supprimé")
                            time.sleep(0.5)
                            st.rerun()
            
            st.divider()
            
            # Ajouter une catégorie
            with st.form("add_category_form"):
                new_category = st.text_input("Nouvelle catégorie")
                
                if st.form_submit_button("➕ Ajouter"):
                    if new_category and new_category not in categories:
                        if add_expense_category(new_category):
                            st.success("✅ Catégorie ajoutée")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.warning("Firebase non disponible")
    
    # Sources de revenus
    with col_rev:
        st.write("**💶 Sources de Revenus**")
        
        if SERVICES_OK:
            sources = get_revenue_sources()
            
            # Afficher les sources
            for source in sources:
                col_name, col_action = st.columns([4, 1])
                with col_name:
                    st.text(f"• {source}")
                with col_action:
                    if st.button("🗑️", key=f"del_source_{source}"):
                        if delete_revenue_source(source):
                            st.success("✅ Supprimé")
                            time.sleep(0.5)
                            st.rerun()
            
            st.divider()
            
            # Ajouter une source
            with st.form("add_source_form"):
                new_source = st.text_input("Nouvelle source")
                
                if st.form_submit_button("➕ Ajouter"):
                    if new_source and new_source not in sources:
                        if add_revenue_source(new_source):
                            st.success("✅ Source ajoutée")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.warning("Firebase non disponible")

# ===== ONGLET 5: THÈME =====
with tabs[4]:
    st.subheader("🎨 Personnalisation du Thème")
    
    col_mode, col_palette = st.columns(2)
    
    with col_mode:
        st.write("**Mode d'affichage**")
        
        new_mode = st.radio(
            "Choisir le mode",
            options=['dark', 'light'],
            format_func=lambda x: '🌙 Mode Sombre' if x == 'dark' else '☀️ Mode Clair',
            index=0 if theme_mode == 'dark' else 1,
            key="theme_mode"
        )
    
    with col_palette:
        st.write("**Palette de couleurs**")
        
        new_palette = st.selectbox(
            "Choisir une palette",
            options=list(PALETTES.keys()),
            index=list(PALETTES.keys()).index(theme_palette),
            key="theme_palette"
        )
        
        # Prévisualisation de la palette
        st.markdown(f"""
        <div class='color-preview'>
            Prévisualisation: {new_palette}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Sauvegarder le thème
    if st.button("💾 Appliquer ce thème", type="primary", use_container_width=True):
        if SERVICES_OK:
            if save_user_theme(st.session_state.user_profile, new_mode, new_palette):
                st.success("✅ Thème enregistré ! Rechargement de la page...")
                time.sleep(1)
                st.rerun()
        else:
            st.warning("Firebase non disponible")
    
    st.info("💡 Le thème sera appliqué uniquement à votre compte")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #707070; font-size: 14px; padding: 20px;'>
    <p>Paramètres - Famileasy v1.0.0</p>
</div>
""", unsafe_allow_html=True)
