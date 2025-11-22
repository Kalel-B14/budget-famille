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
    from parametres_service import get_all_users, get_family_name
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
        transition: all 0.3s ease;
        cursor: pointer;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
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
        
        # Boutons de sélection - Dynamiques
        num_cols = min(len(users_list), 3)
        cols = st.columns(num_cols)
        
        for idx, user in enumerate(users_list):
            with cols[idx % num_cols]:
                user_image = load_profile_image(user) if SERVICES_OK else None
                
                if user_image:
                    st.markdown(f"""
                    <div style='text-align: center; margin: 10px;'>
                        <div style='width: 100px; height: 100px; border-radius: 50%; margin: 0 auto 10px;
                                    overflow: hidden; border: 3px solid #667eea;'>
                            <img src='{user_image}' style='width: 100%; height: 100%; object-fit: cover;'>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button(f"👤 {user}", use_container_width=True, key=f"profile_{user}"):
                    st.session_state.user_profile = user
                    st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #707070; font-size: 14px;'>
            <p>Version 1.0.0 | Fait avec ❤️ pour la famille</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# --- DASHBOARD PRINCIPAL ---
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
    if st.button("⚙️", key="settings_btn", help="Paramètres"):
        st.switch_page("pages/5_⚙️_Parametres.py")

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

# Module Budget
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
```

### **Étape 4 : Commit**

En bas de la page :
- Message : `fix: Ajout roue crantée et système de profils complet`
- Cliquez sur **"Commit changes"**

### **Étape 5 : Attendre le redéploiement**

1. Allez sur votre app Streamlit Cloud
2. Vous verrez **"Updating..."** en bas
3. Attendez **2-3 minutes**
4. Rafraîchissez la page (F5)

### **Étape 6 : Vérifier**

Vous devriez maintenant voir :
- ✅ Une roue crantée ⚙️ en haut à droite
- ✅ Photo de profil à gauche (ou icône 👤)
- ✅ Nom de famille "Famille Duriez"

---

## 🔍 Si ça ne marche toujours pas

**Vérifiez les fichiers sur GitHub :**

Vous devez avoir EXACTEMENT :
```
pages/
├── 5_⚙️_Parametres.py
└── budget_page.py

services/
├── __init__.py
├── firebase.py
├── budget_service.py
├── parametres_service.py
└── utils.py
