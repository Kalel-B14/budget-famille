import streamlit as st
from firebase import get_unread_notifications_count

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
            st.switch_page("streamlit_app.py")

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
        try:
            unread = get_unread_notifications_count()
            if unread > 0:
                st.info(f"🔔 {unread} notification(s)")
        except:
            pass

        # Bouton déconnexion
        if st.button("🚪 Changer de profil", use_container_width=True):
            st.session_state.user_profile = None
            st.session_state.authenticated = False
            st.switch_page("streamlit_app.py")

def check_user_authentication():
    """Vérifie si l'utilisateur est connecté"""
    if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
        st.error("⚠️ Veuillez vous connecter pour accéder à cette page")
        if st.button("Se connecter"):
            st.switch_page("streamlit_app.py")
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