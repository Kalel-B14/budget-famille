import streamlit as st

# Palettes de couleurs
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

def get_theme_styles(mode='dark', palette_name='Violet'):
    """Génère les styles CSS selon le thème choisi"""
    
    palette = PALETTES.get(palette_name, PALETTES['Violet'])
    
    # Couleurs selon le mode
    if mode == 'dark':
        bg_color = '#1a1d24'
        text_color = '#e0e0e0'
        card_bg = 'linear-gradient(135deg, #2d3142 0%, #1f2230 100%)'
        card_hover = 'linear-gradient(135deg, #3d4152 0%, #2d3142 100%)'
        input_bg = '#2d3142'
        border_color = '#3d4152'
    else:  # light
        bg_color = '#f7fafc'
        text_color = '#2d3748'
        card_bg = 'linear-gradient(135deg, #ffffff 0%, #f7fafc 100%)'
        card_hover = 'linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%)'
        input_bg = '#ffffff'
        border_color = '#e2e8f0'
    
    return f"""
    <style>
        /* Configuration de base */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
        }}
        
        /* Cartes */
        .metric-card {{
            background: {card_bg};
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }}
        
        .module-card {{
            background: {card_bg};
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
        }}
        
        .module-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 40px {palette['primary']}80;
            border: 2px solid {palette['primary']};
            background: {card_hover};
        }}
        
        .dashboard-header {{
            background: {palette['gradient']};
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}
        
        /* Boutons */
        .stButton > button {{
            background: {palette['gradient']};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            opacity: 0.9;
            box-shadow: 0 4px 12px {palette['primary']}66;
            transform: translateY(-2px);
        }}
        
        /* Formulaires */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: {bg_color};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {input_bg};
            color: {text_color};
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {palette['gradient']};
            color: white;
        }}
        
        /* Métriques */
        [data-testid="stMetricValue"] {{
            font-size: 28px;
            color: {text_color};
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {text_color};
            opacity: 0.7;
        }}
        
        /* Dataframes */
        .dataframe {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Info/Warning/Error boxes */
        .stAlert {{
            background-color: {input_bg};
            color: {text_color};
            border-left: 4px solid {palette['primary']};
        }}
        
        /* Prévisualisation couleur */
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
    """

def apply_theme(user_profile=None):
    """Applique le thème de l'utilisateur sur toute l'application"""
    try:
        from parametres_service import get_user_theme
        
        if user_profile:
            user_theme = get_user_theme(user_profile)
            mode = user_theme.get('mode', 'dark') if user_theme else 'dark'
            palette = user_theme.get('palette', 'Violet') if user_theme else 'Violet'
        else:
            mode = 'dark'
            palette = 'Violet'
        
        # Appliquer les styles
        st.markdown(get_theme_styles(mode, palette), unsafe_allow_html=True)
        
        return mode, palette
    except:
        # Thème par défaut en cas d'erreur
        st.markdown(get_theme_styles('dark', 'Violet'), unsafe_allow_html=True)
        return 'dark', 'Violet'

def get_palette_colors(palette_name):
    """Retourne les couleurs d'une palette"""
    return PALETTES.get(palette_name, PALETTES['Violet'])
