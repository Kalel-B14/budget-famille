"""
Point d'entrée principal de l'application Famileasy
Ce fichier est détecté automatiquement par Streamlit Cloud
"""

# Simplement importer et exécuter Home.py
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Exécuter Home.py
home_file = current_dir / "Home.py"

if home_file.exists():
    with open(home_file, 'r', encoding='utf-8') as f:
        exec(f.read())
else:
    import streamlit as st
    st.error("⚠️ Le fichier Home.py est introuvable !")
    st.info(f"Chemin recherché : {home_file}")
