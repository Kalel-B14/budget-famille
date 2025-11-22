# 🏠 Famileasy - Application Familiale Multi-Modules

Application web complète pour gérer tous les aspects de votre vie familiale : budget, agenda, courses, galerie photos et plus encore.

## 📁 Structure du Projet

```
Famileasy/
│
├── Home.py                      # Page d'accueil et dashboard principal
│
├── pages/                       # Modules de l'application
│   ├── Budget.py               # Gestion du budget familial ✅
│   ├── Agenda.py               # Calendrier et événements (à venir)
│   ├── Courses.py              # Listes de courses partagées (à venir)
│   ├── Galerie.py              # Galerie photos/vidéos (à venir)
│   ├── Profil.py               # Gestion du profil utilisateur (à venir)
│   └── Parametres.py           # Paramètres de l'application (à venir)
│
├── services/                    # Services et logique métier
│   ├── firebase.py             # Gestion Firebase (auth, database) ✅
│   ├── utils.py                # Utilitaires communs ✅
│   └── budget_service.py       # Logique métier du budget ✅
│
├── requirements.txt             # Dépendances Python ✅
│
└── .streamlit/
    └── secrets.toml            # Configuration Firebase (à créer)
```

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone [votre-repo]
cd Famileasy
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration Firebase

Créez un fichier `.streamlit/secrets.toml` avec vos identifiants Firebase :

```toml
[firebase]
type = "service_account"
project_id = "votre-project-id"
private_key_id = "votre-private-key-id"
private_key = "votre-private-key"
client_email = "votre-client-email"
client_id = "votre-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "votre-client-cert-url"
```

### 4. Lancer l'application

```bash
streamlit run Home.py
```

## 🎨 Fonctionnalités

### ✅ Implémenté

#### 🏠 Page d'Accueil
- **Sélection de profil** : Margaux ou Souliman
- **Dashboard moderne** : Vue d'ensemble de tous les modules
- **Design Dark Mode** : Interface élégante et moderne
- **Statistiques en temps réel** : Aperçu rapide des données

#### 💰 Module Budget
- **Gestion des revenus** : Ajout, modification, suppression
- **Gestion des dépenses** : Catégories personnalisées
- **Tableaux mensuels** : Vue complète par mois avec totaux
- **Graphiques interactifs** :
  - Revenus vs Dépenses
  - Répartition par catégorie
  - Évolution mensuelle
- **Import Excel** : Import en masse de données
- **Notifications** : Suivi des modifications en temps réel
- **Multi-utilisateurs** : Chaque action est tracée
- **Sauvegarde des préférences** : Filtres et sélections mémorisés

### 🔜 À Venir

- 📅 **Agenda** : Calendrier familial partagé
- 🛒 **Courses** : Listes de courses collaboratives
- 📸 **Galerie** : Stockage et partage de photos
- 👤 **Profil** : Gestion des profils utilisateurs
- ⚙️ **Paramètres** : Configuration de l'application

## 🎯 Navigation

### Flux Utilisateur

```
1. Connexion (Home.py)
   ↓
2. Sélection du profil (Margaux/Souliman)
   ↓
3. Dashboard avec tous les modules
   ↓
4. Accès à n'importe quel module
   ↓
5. Bouton "Retour" pour revenir au dashboard
```

### Structure de Navigation

- **Home.py** : Point d'entrée, authentification, dashboard
- **Pages/** : Chaque module est une page indépendante
- **Services/** : Logique métier réutilisable
- **Bouton Retour** : Dans chaque module pour revenir au dashboard

## 💾 Base de Données Firebase

### Collections Firestore

```
expenses/                    # Dépenses
├── [doc_id]
    ├── Catégories: string
    ├── Montant: number
    ├── Fréquence: string
    ├── Description: string
    ├── Mois: string
    ├── Année: number
    ├── Utilisateur: string
    └── Timestamp: number

revenues/                    # Revenus
├── [doc_id]
    ├── Source: string
    ├── Montant: number
    ├── Mois: string
    ├── Année: number
    ├── Utilisateur: string
    └── Timestamp: number

notifications/               # Notifications
├── [doc_id]
    ├── title: string
    ├── message: string
    ├── user: string
    ├── module: string
    ├── timestamp: number
    └── read: boolean

user_profiles/              # Profils utilisateurs
├── Margaux
│   └── profile_image: string (base64)
└── Souliman
    └── profile_image: string (base64)

user_preferences/           # Préférences utilisateurs
├── Margaux
│   ├── budget_year: number
│   └── budget_months: array
└── Souliman
    ├── budget_year: number
    └── budget_months: array
```

## 🔐 Sécurité

- **Authentification par profil** : Sélection simple pour usage familial
- **Traçabilité** : Toutes les actions sont associées à un utilisateur
- **Notifications** : Historique complet des modifications
- **Pas de stockage local** : Toutes les données dans Firebase

## 🎨 Design

### Thème Dark Mode
- **Couleurs principales** : Violet (#667eea) et Mauve (#764ba2)
- **Background** : Gris foncé (#1a1d24)
- **Cartes** : Gradients subtils avec ombres
- **Typographie** : Claire et lisible
- **Animations** : Effets hover et transitions smooth

### Responsive
- Layout adaptatif avec colonnes Streamlit
- Optimisé pour desktop (tablette et mobile à venir)

## 📊 Module Budget - Détails

### Catégories de Dépenses

```python
- Compte Perso (Souliman, Margaux)
- Habitation (Loyer, Charges)
- Énergie (Engie, Veolia)
- Transport (Essence, Crédit Voiture, Assurance)
- Communications (Forfaits Internet, Mobile)
- Crédits (Voiture, Consommation)
- Famille (Olga, École Clémence, Épargne Clémence)
- Courses
- Divers (Anniversaires, Marge compte, Autre)
```

### Format Import Excel

**Dépenses** :
```
Catégorie | Montant | Fréquence | Mois | Année | Description
```

**Revenus** :
```
Source | Montant | Mois | Année
```

## 🛠️ Technologies

- **Frontend** : Streamlit
- **Backend** : Python
- **Database** : Firebase Firestore
- **Graphiques** : Plotly
- **Data** : Pandas
- **Import** : Openpyxl

## 📝 Développement

### Ajouter un Nouveau Module

1. Créer `pages/NouveauModule.py`
2. Créer `services/nouveau_service.py` (si nécessaire)
3. Importer les services Firebase et utils
4. Utiliser `check_user_authentication()` en début de page
5. Ajouter un bouton "Retour" vers Home.py
6. Ajouter la carte du module dans `Home.py`

### Exemple de Structure de Page

```python
import streamlit as st
from services.firebase import init_firebase
from services.utils import check_user_authentication, apply_dark_theme

st.set_page_config(page_title="Mon Module", layout="wide")

init_firebase()
check_user_authentication()
apply_dark_theme()

# Bouton retour
if st.button("← Retour"):
    st.switch_page("Home.py")

# Votre contenu ici
st.title("Mon Module")
```

## 🐛 Debug

- Logs Firebase dans la console
- Messages d'erreur Streamlit clairs
- Vérification des données avec `st.write()`

## 📦 Déploiement

### Streamlit Cloud

1. Push sur GitHub
2. Connecter à Streamlit Cloud
3. Ajouter les secrets Firebase
4. Déployer

## 👥 Contributeurs

- Développé pour la famille Martin

## 📄 Licence

Projet personnel - Tous droits réservés

## 🔄 Versions

- **v1.0.0** : Module Budget complet avec notifications
- **v0.9.0** : Page d'accueil et authentification
- **v0.1.0** : Structure initiale du projet

---

Made with ❤️ for family management
