"""
Point d'entrée principal de l'application Famileasy
Ce fichier est détecté automatiquement par Streamlit Cloud
"""

# Simplement importer et exécuter streamlit_app.py
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Exécuter streamlit_app.py
app_file = current_dir / "streamlit_app.py"

if app_file.exists():
    with open(app_file, 'r', encoding='utf-8') as f:
        exec(f.read())
else:
    import streamlit as st
    st.error("⚠️ Le fichier streamlit_app.py est introuvable !")
    st.info(f"Chemin recherché : {app_file}")
