"""
Gestionnaire de thème global pour Famileasy
"""

import streamlit as st

try:
    from firebase_admin import firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

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
    """Initialise le thème"""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'
    if 'theme_color' not in st.session_state:
        st.session_state.theme_color = 'Violet'
    if 'theme_initialized' not in st.session_state:
        st.session_state.theme_initialized = False


def load_user_theme_preferences(username):
    """Charge les préférences depuis Firebase"""
    if not FIREBASE_AVAILABLE:
        return
    
    try:
        db = firestore.client()
        theme_ref = db.collection('user_theme_preferences').document(username)
        theme_doc = theme_ref.get()
        
        if theme_doc.exists:
            theme_data = theme_doc.to_dict()
            st.session_state.theme_mode = theme_data.get('mode', 'dark')
            st.session_state.theme_color = theme_data.get('color', 'Violet')
        
        st.session_state.theme_initialized = True
    except Exception as e:
        print(f"Erreur chargement thème: {e}")


def save_user_theme_preferences(username, mode, color):
    """Sauvegarde dans Firebase"""
    if not FIREBASE_AVAILABLE:
        return False
    
    try:
        db = firestore.client()
        theme_ref = db.collection('user_theme_preferences').document(username)
        theme_ref.set({
            'mode': mode,
            'color': color,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")
        return False


def get_theme_colors():
    """Retourne les couleurs actuelles"""
    color_name = st.session_state.get('theme_color', 'Violet')
    return COULEURS_DISPONIBLES.get(color_name, COULEURS_DISPONIBLES['Violet'])


def apply_global_theme():
    """Applique le thème CSS"""
    init_theme_state()
    
    if 'user_profile' in st.session_state and st.session_state.user_profile:
        if not st.session_state.get('theme_initialized', False):
            load_user_theme_preferences(st.session_state.user_profile)
    
    colors = get_theme_colors()
    mode = st.session_state.get('theme_mode', 'dark')
    
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
    
    st.markdown(f"""
    <style>
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
        
        .stApp {{
            background-color: var(--bg-color) !important;
        }}
        
        [data-testid="stSidebar"] {{
            background-color: var(--secondary-bg) !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color) !important;
        }}
        
        p, span, div, label {{
            color: var(--text-color) !important;
        }}
        
        [data-testid="stMetric"] {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            padding: 20px !important;
            border-radius: 10px !important;
        }}
        
        [data-testid="stMetric"] label, 
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: white !important;
        }}
        
        .stButton button {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
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
        
        .stTextInput input, .stNumberInput input, .stSelectbox select {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--secondary-bg) !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: var(--text-color) !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
        }}
        
        .dashboard-card {{
            background: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            min-height: 150px !important;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-5px) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
            border-color: var(--primary-color) !important;
        }}
        
        .dashboard-card h3 {{
            color: var(--primary-color) !important;
        }}
        
        .header-container {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            border-radius: 20px !important;
            padding: 30px !important;
            margin-bottom: 30px !important;
        }}
        
        .header-container h1 {{
            color: white !important;
        }}
        
        .profile-picture {{
            width: 50px !important;
            height: 50px !important;
            border-radius: 50% !important;
            border: 3px solid white !important;
            object-fit: cover !important;
        }}
        
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
        
        ::-webkit-scrollbar {{
            width: 10px !important;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--secondary-bg) !important;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color) !important;
            border-radius: 5px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def create_theme_selector():
    """Sélecteur de thème dans la sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Thème")
    
    current_mode = st.session_state.get('theme_mode', 'dark')
    mode_options = {"Mode Sombre 🌙": "dark", "Mode Clair ☀️": "light"}
    
    selected = st.sidebar.radio(
        "Mode d'affichage",
        list(mode_options.keys()),
        index=0 if current_mode == "dark" else 1,
        key="theme_mode_selector"
    )
    new_mode = mode_options[selected]
    
    current_color = st.session_state.get('theme_color', 'Violet')
    new_color = st.sidebar.selectbox(
        "Couleur primaire",
        list(COULEURS_DISPONIBLES.keys()),
        index=list(COULEURS_DISPONIBLES.keys()).index(current_color),
        key="theme_color_selector"
    )
    
    if new_mode != st.session_state.theme_mode or new_color != st.session_state.theme_color:
        st.session_state.theme_mode = new_mode
        st.session_state.theme_color = new_color
        
        if 'user_profile' in st.session_state and st.session_state.user_profile:
            if save_user_theme_preferences(st.session_state.user_profile, new_mode, new_color):
                st.sidebar.success("✅ Thème sauvegardé")
        
        st.rerun()
    
    colors = get_theme_colors()
    st.sidebar.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
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