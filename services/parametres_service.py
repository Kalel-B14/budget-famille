from firebase_admin import firestore
import time

def get_db():
    """Retourne l'instance Firestore"""
    try:
        return firestore.client()
    except:
        return None

# ===== GESTION DES UTILISATEURS =====

def get_all_users():
    """Récupère la liste de tous les utilisateurs"""
    db = get_db()
    if not db:
        return ['Margaux', 'Souliman']  # Valeurs par défaut
    
    try:
        config_ref = db.collection('config').document('users')
        doc = config_ref.get()
        
        if doc.exists:
            return doc.to_dict().get('list', ['Margaux', 'Souliman'])
        else:
            # Créer la configuration initiale
            config_ref.set({'list': ['Margaux', 'Souliman']})
            return ['Margaux', 'Souliman']
    except:
        return ['Margaux', 'Souliman']

def add_user(username):
    """Ajoute un nouvel utilisateur"""
    db = get_db()
    if not db:
        return False
    
    try:
        users = get_all_users()
        if username not in users:
            users.append(username)
            config_ref = db.collection('config').document('users')
            config_ref.set({'list': users})
            
            # Créer un profil vide pour le nouvel utilisateur
            profile_ref = db.collection('user_profiles').document(username)
            profile_ref.set({
                'created_at': time.time(),
                'profile_image': None
            })
            
            return True
        return False
    except:
        return False

def delete_user(username):
    """Supprime un utilisateur"""
    db = get_db()
    if not db:
        return False
    
    try:
        users = get_all_users()
        if username in users and len(users) > 2:  # Garder au moins 2 utilisateurs
            users.remove(username)
            config_ref = db.collection('config').document('users')
            config_ref.set({'list': users})
            
            # Optionnel: supprimer le profil utilisateur
            # db.collection('user_profiles').document(username).delete()
            
            return True
        return False
    except:
        return False

# ===== GESTION NOM DE FAMILLE =====

def get_family_name():
    """Récupère le nom de famille"""
    db = get_db()
    if not db:
        return "Famille Duriez"
    
    try:
        config_ref = db.collection('config').document('family')
        doc = config_ref.get()
        
        if doc.exists:
            return doc.to_dict().get('name', 'Famille Duriez')
        else:
            # Créer la configuration initiale
            config_ref.set({'name': 'Famille Duriez'})
            return 'Famille Duriez'
    except:
        return "Famille Duriez"

def set_family_name(name):
    """Modifie le nom de famille"""
    db = get_db()
    if not db:
        return False
    
    try:
        config_ref = db.collection('config').document('family')
        config_ref.set({'name': name})
        return True
    except:
        return False

# ===== GESTION CATÉGORIES BUDGET =====

DEFAULT_EXPENSE_CATEGORIES = [
    'Compte Perso - Souliman', 'Compte Perso - Margaux', 'Essence', 'Loyer',
    'Forfait Internet', 'Forfait Mobile', 'Crédit Voiture',
    'Frais Bourso (Voitures, Maison, Hopital...)', 'Crédit Consomation',
    'Engie (chauffage + élec)', 'Veolia (eau)', 'Assurance Maison',
    'Frais Voiture (Réparation, Assurance...)', 'Anniversaires (Fêtes Noël, pacques...)',
    'Olga', 'Épargne', 'École Clémence', 'Épargne Clémence', 'Marge compte',
    'Courses', 'Autre'
]

DEFAULT_REVENUE_SOURCES = [
    'Salaire Principal',
    'Salaire Conjoint',
    'Primes',
    'Revenus Complémentaires',
    'Autre'
]

def get_expense_categories():
    """Récupère les catégories de dépenses"""
    db = get_db()
    if not db:
        return DEFAULT_EXPENSE_CATEGORIES
    
    try:
        config_ref = db.collection('config').document('budget')
        doc = config_ref.get()
        
        if doc.exists:
            return doc.to_dict().get('expense_categories', DEFAULT_EXPENSE_CATEGORIES)
        else:
            # Créer la configuration initiale
            config_ref.set({
                'expense_categories': DEFAULT_EXPENSE_CATEGORIES,
                'revenue_sources': DEFAULT_REVENUE_SOURCES
            })
            return DEFAULT_EXPENSE_CATEGORIES
    except:
        return DEFAULT_EXPENSE_CATEGORIES

def add_expense_category(category):
    """Ajoute une catégorie de dépense"""
    db = get_db()
    if not db:
        return False
    
    try:
        categories = get_expense_categories()
        if category not in categories:
            categories.append(category)
            config_ref = db.collection('config').document('budget')
            config_ref.update({'expense_categories': categories})
            return True
        return False
    except:
        return False

def delete_expense_category(category):
    """Supprime une catégorie de dépense"""
    db = get_db()
    if not db:
        return False
    
    try:
        categories = get_expense_categories()
        if category in categories and category != 'Autre':  # Ne pas supprimer "Autre"
            categories.remove(category)
            config_ref = db.collection('config').document('budget')
            config_ref.update({'expense_categories': categories})
            return True
        return False
    except:
        return False

def get_revenue_sources():
    """Récupère les sources de revenus"""
    db = get_db()
    if not db:
        return DEFAULT_REVENUE_SOURCES
    
    try:
        config_ref = db.collection('config').document('budget')
        doc = config_ref.get()
        
        if doc.exists:
            return doc.to_dict().get('revenue_sources', DEFAULT_REVENUE_SOURCES)
        else:
            return DEFAULT_REVENUE_SOURCES
    except:
        return DEFAULT_REVENUE_SOURCES

def add_revenue_source(source):
    """Ajoute une source de revenu"""
    db = get_db()
    if not db:
        return False
    
    try:
        sources = get_revenue_sources()
        if source not in sources:
            sources.append(source)
            config_ref = db.collection('config').document('budget')
            config_ref.update({'revenue_sources': sources})
            return True
        return False
    except:
        return False

def delete_revenue_source(source):
    """Supprime une source de revenu"""
    db = get_db()
    if not db:
        return False
    
    try:
        sources = get_revenue_sources()
        if source in sources and source != 'Autre':  # Ne pas supprimer "Autre"
            sources.remove(source)
            config_ref = db.collection('config').document('budget')
            config_ref.update({'revenue_sources': sources})
            return True
        return False
    except:
        return False

# ===== GESTION THÈMES =====

def get_user_theme(user):
    """Récupère le thème de l'utilisateur"""
    db = get_db()
    if not db:
        return {'mode': 'dark', 'palette': 'Violet'}
    
    try:
        theme_ref = db.collection('user_themes').document(user)
        doc = theme_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            # Thème par défaut
            default_theme = {'mode': 'dark', 'palette': 'Violet'}
            theme_ref.set(default_theme)
            return default_theme
    except:
        return {'mode': 'dark', 'palette': 'Violet'}

def save_user_theme(user, mode, palette):
    """Sauvegarde le thème de l'utilisateur"""
    db = get_db()
    if not db:
        return False
    
    try:
        theme_ref = db.collection('user_themes').document(user)
        theme_ref.set({
            'mode': mode,
            'palette': palette,
            'updated_at': time.time()
        })
        return True
    except:
        return False
