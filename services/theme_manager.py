"""
Gestionnaire de thème global pour l'application Famileasy
Ce module gère les préférences de thème (clair/sombre) et de couleur primaire
"""

import streamlit as st
from services.firebase import init_firebase, get_firestore_client

# Couleurs disponibles
COULEURS_DISPONIBLES = {
    "Violet": {"primary": "#667eea", "secondary": "#764ba2"},
    "Bleu": {"primary": "#4A90E2", "secondary": "#2E5C8A"},
    "Vert": {"primary": "#48BB78", "secondary": "#2F855A"},
    "Rose": {"primary": "#ED64A6", "secondary": "#B83280"},
    "Orange": {"primary": "#ED8936", "secondary": "#C05621"},
    "Rouge": {"primary": "#F56565", "secondary": "#C53030"},
    "Turquoise": {"primary": "#38B2AC", "secondary": "#2C7A7B"},
    "Indigo": {"primary": "#5A67D8", "secondary": "#434190"},
}

def init_theme_state():
    """Initialise l'état du thème dans session_state"""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'  # Mode sombre par défaut
    
    if 'theme_color' not in st.session_state:
        st.session_state.theme_color = 'Violet'  # Couleur par défaut
    
    if 'theme_initialized' not in st.session_state:
        st.session_state.theme_initialized = False

def load_user_theme_preferences(username):
    """Charge les préférences de thème de l'utilisateur depuis Firebase"""
    try:
        db = get_firestore_client()
        if db is None:
            return
        
        # Charger les préférences de thème
        theme_ref = db.collection('user_theme_preferences').document(username)
        theme_doc = theme_ref.get()
        
        if theme_doc.exists:
            theme_data = theme_doc.to_dict()
            st.session_state.theme_mode = theme_data.get('mode', 'dark')
            st.session_state.theme_color = theme_data.get('color', 'Violet')
        
        st.session_state.theme_initialized = True
        
    except Exception as e:
        print(f"Erreur lors du chargement des préférences de thème: {e}")

def save_user_theme_preferences(username, mode, color):
    """Sauvegarde les préférences de thème de l'utilisateur dans Firebase"""
    try:
        db = get_firestore_client()
        if db is None:
            return False
        
        theme_ref = db.collection('user_theme_preferences').document(username)
        theme_ref.set({
            'mode': mode,
            'color': color,
            'updated_at': st.session_state.get('timestamp', 0)
        })
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des préférences de thème: {e}")
        return False

def get_theme_colors():
    """Retourne les couleurs du thème actuel"""
    color_name = st.session_state.get('theme_color', 'Violet')
    return COULEURS_DISPONIBLES.get(color_name, COULEURS_DISPONIBLES['Violet'])

def apply_global_theme():
    """Applique le thème global à toute l'application avec CSS personnalisé"""
    
    # Initialiser le thème si ce n'est pas fait
    init_theme_state()
    
    # Charger les préférences si l'utilisateur est connecté
    if 'user_profile' in st.session_state and st.session_state.user_profile:
        if not st.session_state.get('theme_initialized', False):
            load_user_theme_preferences(st.session_state.user_profile)
    
    # Obtenir les couleurs
    colors = get_theme_colors()
    mode = st.session_state.get('theme_mode', 'dark')
    
    # Couleurs en fonction du mode
    if mode == 'dark':
        bg_color = "#0e1117"
        secondary_bg = "#1a1d24"
        card_bg = "#1f2230"
        text_color = "#ffffff"
        text_secondary = "#a0a0a0"
        border_color = "#2d3142"
    else:
        bg_color = "#ffffff"
        secondary_bg = "#f0f2f6"
        card_bg = "#ffffff"
        text_color = "#000000"
        text_secondary = "#666666"
        border_color = "#e0e0e0"
    
    # CSS global
    st.markdown(f"""
    <style>
        /* === VARIABLES CSS === */
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --bg-color: {bg_color};
            --secondary-bg: {secondary_bg};
            --card-bg: {card_bg};
            --text-color: {text_color};
            --text-secondary: {text_secondary};
            --border-color: {border_color};
        }}
        
        /* === BACKGROUND PRINCIPAL === */
        .stApp {{
            background-color: var(--bg-color) !important;
        }}
        
        /* === SIDEBAR === */
        [data-testid="stSidebar"] {{
            background-color: var(--secondary-bg) !important;
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: var(--text-color) !important;
        }}
        
        /* === HEADER / TITRE === */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color) !important;
        }}
        
        /* === TEXTE === */
        p, span, div {{
            color: var(--text-color) !important;
        }}
        
        /* === CARTES / CONTAINERS === */
        [data-testid="stVerticalBlock"] > div {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
        }}
        
        /* === MÉTRIQUES === */
        [data-testid="stMetric"] {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
            padding: 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }}
        
        [data-testid="stMetric"] label {{
            color: white !important;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: white !important;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            color: white !important;
        }}
        
        /* === BOUTONS === */
        .stButton button {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important;
        }}
        
        /* === INPUTS === */
        .stTextInput input, .stNumberInput input, .stSelectbox select {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        /* === DATAFRAME === */
        [data-testid="stDataFrame"] {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
        }}
        
        .stDataFrame table {{
            color: var(--text-color) !important;
        }}
        
        /* === TABS === */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--secondary-bg) !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: var(--text-color) !important;
            background-color: var(--card-bg) !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
            color: white !important;
        }}
        
        /* === EXPANDER === */
        .streamlit-expanderHeader {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
        }}
        
        /* === CARTES PERSONNALISÉES === */
        .dashboard-card {{
            background: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            height: 100% !important;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-5px) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
            border-color: var(--primary-color) !important;
        }}
        
        .dashboard-card h3 {{
            color: var(--primary-color) !important;
            margin-bottom: 10px !important;
        }}
        
        .dashboard-card p {{
            color: var(--text-secondary) !important;
        }}
        
        /* === HEADER AVEC PHOTO DE PROFIL === */
        .header-container {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
            border-radius: 20px !important;
            padding: 30px !important;
            margin-bottom: 30px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }}
        
        .header-container h1 {{
            color: white !important;
            margin: 0 !important;
        }}
        
        .profile-picture {{
            width: 50px !important;
            height: 50px !important;
            border-radius: 50% !important;
            border: 3px solid white !important;
            cursor: pointer !important;
            transition: transform 0.3s ease !important;
        }}
        
        .profile-picture:hover {{
            transform: scale(1.1) !important;
        }}
        
        /* === NOTIFICATIONS === */
        .notification-panel {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            max-height: 400px !important;
            overflow-y: auto !important;
        }}
        
        .notification-item {{
            background-color: var(--secondary-bg) !important;
            border-left: 3px solid var(--primary-color) !important;
            padding: 10px !important;
            border-radius: 8px !important;
            margin-bottom: 10px !important;
        }}
        
        .notification-item.unread {{
            border-left-color: #ff4444 !important;
            font-weight: 600 !important;
        }}
        
        /* === ANIMATIONS === */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .animate-in {{
            animation: slideIn 0.5s ease-out !important;
        }}
        
        /* === SCROLLBAR === */
        ::-webkit-scrollbar {{
            width: 10px !important;
            height: 10px !important;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--secondary-bg) !important;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color) !important;
            border-radius: 5px !important;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--secondary-color) !important;
        }}
        
        /* === GRAPHIQUES PLOTLY === */
        .js-plotly-plot {{
            background-color: var(--card-bg) !important;
        }}
        
        /* === DIVIDER === */
        hr {{
            border-color: var(--border-color) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_theme_selector():
    """Crée un sélecteur de thème dans la sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Thème")
    
    # Mode clair/sombre
    current_mode = st.session_state.get('theme_mode', 'dark')
    mode_options = {"Mode Sombre 🌙": "dark", "Mode Clair ☀️": "light"}
    current_mode_label = "Mode Sombre 🌙" if current_mode == "dark" else "Mode Clair ☀️"
    
    selected_mode_label = st.sidebar.radio(
        "Mode d'affichage",
        options=list(mode_options.keys()),
        index=0 if current_mode == "dark" else 1,
        key="theme_mode_selector"
    )
    
    new_mode = mode_options[selected_mode_label]
    
    # Couleur primaire
    current_color = st.session_state.get('theme_color', 'Violet')
    new_color = st.sidebar.selectbox(
        "Couleur primaire",
        options=list(COULEURS_DISPONIBLES.keys()),
        index=list(COULEURS_DISPONIBLES.keys()).index(current_color),
        key="theme_color_selector"
    )
    
    # Sauvegarder si changement
    if new_mode != st.session_state.theme_mode or new_color != st.session_state.theme_color:
        st.session_state.theme_mode = new_mode
        st.session_state.theme_color = new_color
        
        # Sauvegarder dans Firebase
        if 'user_profile' in st.session_state and st.session_state.user_profile:
            if save_user_theme_preferences(
                st.session_state.user_profile,
                new_mode,
                new_color
            ):
                st.sidebar.success("✅ Thème sauvegardé")
        
        st.rerun()
    
    # Aperçu des couleurs
    colors = get_theme_colors()
    st.sidebar.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
            margin-top: 10px;
        '>
            Aperçu du thème
        </div>
        """,
        unsafe_allow_html=True
    )