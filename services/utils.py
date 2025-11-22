import streamlit as st
from firebase import get_unread_notifications_count

def apply_dark_theme():
    """Applique le thème sombre à l'application"""
    st.markdown("""
    <style>
        /* Dark Theme */
        .stApp {
            background-color: #1a1d24;
            color: #e0e0e0;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #ffffff !important;
        }
        
        /* Cards style */
        .metric-card {
            background: linear-gradient(135deg, #2d3142 0%, #1f2230 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }
        
        /* Buttons */
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
        
        /* Tables */
        .dataframe {
            background-color: #2d3142 !important;
            color: #e0e0e0 !important;
        }
        
        /* Forms */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #2d3142;
            color: #e0e0e0;
            border: 1px solid #3d4152;
            border-radius: 8px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #1a1d24;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #2d3142;
            color: #e0e0e0;
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 28px;
            color: #ffffff;
        }
        
        [data-testid="stMetricLabel"] {
            color: #a0a0a0;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1f2230;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)

def format_currency(amount):
    """Formate un montant en euros"""
    return f"{amount:,.2f} €".replace(",", " ")

def format_date(timestamp):
    """Formate un timestamp en date lisible"""
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")

def create_sidebar_navigation():
    """Crée une barre latérale de navigation commune"""
    with st.sidebar:
        st.markdown("### 🏠 Navigation")
        
        if st.button("🏠 Accueil", use_container_width=True):
            st.switch_page("Home.py")
        
        st.divider()
        
        st.markdown("### 📱 Modules")
        
        if st.button("💰 Budget", use_container_width=True):
            st.switch_page("pages/Budget.py")
        
        if st.button("📅 Agenda", use_container_width=True):
            st.switch_page("pages/Agenda.py")
        
        if st.button("🛒 Courses", use_container_width=True):
            st.switch_page("pages/Courses.py")
        
        if st.button("📸 Galerie", use_container_width=True):
            st.switch_page("pages/Galerie.py")
        
        st.divider()
        
        if st.button("👤 Profil", use_container_width=True):
            st.switch_page("pages/Profil.py")
        
        if st.button("⚙️ Paramètres", use_container_width=True):
            st.switch_page("pages/Parametres.py")
        
        st.divider()
        
        # Afficher les notifications
        unread = get_unread_notifications_count()
        if unread > 0:
            st.info(f"🔔 {unread} notification(s)")
        
        # Bouton déconnexion
        if st.button("🚪 Changer de profil", use_container_width=True):
            st.session_state.user_profile = None
            st.switch_page("Home.py")

def check_user_authentication():
    """Vérifie si l'utilisateur est connecté"""
    if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
        st.error("⚠️ Veuillez vous connecter pour accéder à cette page")
        if st.button("Se connecter"):
            st.switch_page("Home.py")
        st.stop()
        return False
    return True

def create_module_header(module_name, icon):
    """Crée un en-tête standardisé pour chaque module"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{icon} {module_name}")
    with col2:
        st.write(f"**Connecté:** {st.session_state.get('user_profile', 'Invité')}")
