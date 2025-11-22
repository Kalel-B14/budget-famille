from firebase_admin import firestore
import time
import streamlit as st

# Liste des catégories de dépenses
CATEGORIES_DEPENSES = [
    'Compte Perso - Souliman', 'Compte Perso - Margaux', 'Essence', 'Loyer',
    'Forfait Internet', 'Forfait Mobile', 'Crédit Voiture',
    'Frais Bourso (Voitures, Maison, Hopital...)', 'Crédit Consomation',
    'Engie (chauffage + élec)', 'Veolia (eau)', 'Assurance Maison',
    'Frais Voiture (Réparation, Assurance...)', 'Anniversaires (Fêtes Noël, pacques...)',
    'Olga', 'Épargne', 'École Clémence', 'Épargne Clémence', 'Marge compte',
    'Courses', 'Autre'
]

def get_db():
    """Retourne l'instance Firestore"""
    try:
        return firestore.client()
    except:
        return None

def add_notification(title, message, user, module="budget"):
    """Ajoute une notification"""
    db = get_db()
    if not db:
        return
    try:
        notif_ref = db.collection('notifications').document()
        notif_ref.set({
            'title': title,
            'message': message,
            'user': user,
            'module': module,
            'timestamp': time.time(),
            'read': False
        })
    except:
        pass

# ===== GESTION DES DÉPENSES =====

def add_expense(category, amount, frequency, description, month, year, user):
    """Ajoute une dépense à Firestore"""
    db = get_db()
    if not db:
        return False
    
    try:
        expense_ref = db.collection('expenses').document()
        expense_ref.set({
            'Catégories': category,
            'Montant': float(amount),
            'Fréquence': frequency,
            'Description': description,
            'Mois': month,
            'Année': int(year),
            'Utilisateur': user,
            'Timestamp': time.time()
        })
        
        # Notification
        add_notification(
            "Dépense ajoutée", 
            f"{user} a ajouté {amount:.0f}€ dans {category} pour {month} {year}", 
            user
        )
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'ajout: {str(e)}")
        return False

def update_expense(doc_id, category, amount, frequency, description, month, year, user):
    """Met à jour une dépense"""
    db = get_db()
    if not db:
        return False
    
    try:
        expense_ref = db.collection('expenses').document(doc_id)
        expense_ref.update({
            'Catégories': category,
            'Montant': float(amount),
            'Fréquence': frequency,
            'Description': description,
            'Mois': month,
            'Année': int(year),
            'ModifiéPar': user,
            'DateModification': time.time()
        })
        
        # Notification
        add_notification(
            "Dépense modifiée", 
            f"{user} a modifié une dépense de {amount:.0f}€ dans {category}", 
            user
        )
        return True
    except:
        return False

def delete_expense(doc_id, user, category, amount):
    """Supprime une dépense"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.collection('expenses').document(doc_id).delete()
        
        # Notification
        add_notification(
            "Dépense supprimée", 
            f"{user} a supprimé une dépense de {amount:.0f}€ dans {category}", 
            user
        )
        return True
    except:
        return False

def fetch_expenses():
    """Récupère toutes les dépenses avec leurs IDs"""
    db = get_db()
    if not db:
        return []
    
    try:
        expenses_ref = db.collection('expenses')
        docs = expenses_ref.stream()
        expenses = []
        for doc in docs:
            data = doc.to_dict()
            data['doc_id'] = doc.id
            expenses.append(data)
        return expenses
    except:
        return []

# ===== GESTION DES REVENUS =====

def add_revenue(source, amount, month, year, user):
    """Ajoute un revenu à Firestore"""
    db = get_db()
    if not db:
        return False
    
    try:
        revenue_ref = db.collection('revenues').document()
        revenue_ref.set({
            'Source': source,
            'Montant': float(amount),
            'Mois': month,
            'Année': int(year),
            'Utilisateur': user,
            'Timestamp': time.time()
        })
        
        # Notification
        add_notification(
            "Revenu ajouté", 
            f"{user} a ajouté {amount:.0f}€ de {source} pour {month} {year}", 
            user
        )
        return True
    except:
        return False

def update_revenue(doc_id, source, amount, month, year, user):
    """Met à jour un revenu"""
    db = get_db()
    if not db:
        return False
    
    try:
        revenue_ref = db.collection('revenues').document(doc_id)
        revenue_ref.update({
            'Source': source,
            'Montant': float(amount),
            'Mois': month,
            'Année': int(year),
            'ModifiéPar': user,
            'DateModification': time.time()
        })
        
        # Notification
        add_notification(
            "Revenu modifié", 
            f"{user} a modifié un revenu de {amount:.0f}€ de {source}", 
            user
        )
        return True
    except:
        return False

def delete_revenue(doc_id, user, source, amount):
    """Supprime un revenu"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.collection('revenues').document(doc_id).delete()
        
        # Notification
        add_notification(
            "Revenu supprimé", 
            f"{user} a supprimé un revenu de {amount:.0f}€ de {source}", 
            user
        )
        return True
    except:
        return False

def fetch_revenues():
    """Récupère tous les revenus avec leurs IDs"""
    db = get_db()
    if not db:
        return []
    
    try:
        revenues_ref = db.collection('revenues')
        docs = revenues_ref.stream()
        revenues = []
        for doc in docs:
            data = doc.to_dict()
            data['doc_id'] = doc.id
            revenues.append(data)
        return revenues
    except:
        return []
