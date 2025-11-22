from firebase_admin import firestore
import time
from firebase import add_notification

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
    return firestore.client()

# ===== GESTION DES DÉPENSES =====

def add_expense(category, amount, frequency, description, month, year, user, timestamp=None):
    """Ajoute une dépense à Firestore"""
    db = get_db()
    expense_ref = db.collection('expenses').document()
    expense_ref.set({
        'Catégories': category,
        'Montant': float(amount),
        'Fréquence': frequency,
        'Description': description,
        'Mois': month,
        'Année': int(year),
        'Utilisateur': user,
        'Timestamp': timestamp if timestamp else time.time()
    })
    # Notification
    add_notification(
        "Dépense ajoutée", 
        f"{user} a ajouté {amount}€ dans {category} pour {month} {year}", 
        user, 
        "budget"
    )

def update_expense(doc_id, category, amount, frequency, description, month, year, user):
    """Met à jour une dépense"""
    db = get_db()
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
        f"{user} a modifié une dépense de {amount}€ dans {category}", 
        user, 
        "budget"
    )

def delete_expense(doc_id, user, category, amount):
    """Supprime une dépense"""
    db = get_db()
    db.collection('expenses').document(doc_id).delete()
    # Notification
    add_notification(
        "Dépense supprimée", 
        f"{user} a supprimé une dépense de {amount}€ dans {category}", 
        user, 
        "budget"
    )

def fetch_expenses():
    """Récupère toutes les dépenses avec leurs IDs"""
    db = get_db()
    expenses_ref = db.collection('expenses')
    docs = expenses_ref.stream()
    expenses = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        expenses.append(data)
    return expenses

# ===== GESTION DES REVENUS =====

def add_revenue(source, amount, month, year, user, timestamp=None):
    """Ajoute un revenu à Firestore"""
    db = get_db()
    revenue_ref = db.collection('revenues').document()
    revenue_ref.set({
        'Source': source,
        'Montant': float(amount),
        'Mois': month,
        'Année': int(year),
        'Utilisateur': user,
        'Timestamp': timestamp if timestamp else time.time()
    })
    # Notification
    add_notification(
        "Revenu ajouté", 
        f"{user} a ajouté {amount}€ de {source} pour {month} {year}", 
        user, 
        "budget"
    )

def update_revenue(doc_id, source, amount, month, year, user):
    """Met à jour un revenu"""
    db = get_db()
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
        f"{user} a modifié un revenu de {amount}€ de {source}", 
        user, 
        "budget"
    )

def delete_revenue(doc_id, user, source, amount):
    """Supprime un revenu"""
    db = get_db()
    db.collection('revenues').document(doc_id).delete()
    # Notification
    add_notification(
        "Revenu supprimé", 
        f"{user} a supprimé un revenu de {amount}€ de {source}", 
        user, 
        "budget"
    )

def fetch_revenues():
    """Récupère tous les revenus avec leurs IDs"""
    db = get_db()
    revenues_ref = db.collection('revenues')
    docs = revenues_ref.stream()
    revenues = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        revenues.append(data)
    return revenues

# ===== IMPORT EXCEL =====

def import_expenses_from_excel(df, default_year, user):
    """Importe des dépenses depuis un DataFrame Excel"""
    imported_count = 0
    for _, row in df.iterrows():
        categorie = str(row.get('Catégorie', row.get('Catégories', 'Autre'))).strip()
        
        # Vérifier si la catégorie existe
        if categorie not in CATEGORIES_DEPENSES:
            categorie = 'Autre'
        
        add_expense(
            categorie,
            float(row.get('Montant', 0)),
            row.get('Fréquence', 'Unique'),
            row.get('Description', ''),
            row.get('Mois', 'Janvier'),
            int(row.get('Année', row.get('Annee', default_year))),
            user
        )
        imported_count += 1
    
    return imported_count

def import_revenues_from_excel(df, default_year, user):
    """Importe des revenus depuis un DataFrame Excel"""
    imported_count = 0
    for _, row in df.iterrows():
        add_revenue(
            row.get('Source', 'Autre'),
            float(row.get('Montant', 0)),
            row.get('Mois', 'Janvier'),
            int(row.get('Année', row.get('Annee', default_year))),
            user
        )
        imported_count += 1
    
    return imported_count

# ===== STATISTIQUES =====

def get_budget_summary(year, months=None):
    """Récupère un résumé du budget pour une année et des mois donnés"""
    expenses = fetch_expenses()
    revenues = fetch_revenues()
    
    import pandas as pd
    
    df_expenses = pd.DataFrame(expenses)
    df_revenues = pd.DataFrame(revenues)
    
    # Filtrer par année
    if not df_expenses.empty:
        df_expenses = df_expenses[df_expenses['Année'] == year]
    if not df_revenues.empty:
        df_revenues = df_revenues[df_revenues['Année'] == year]
    
    # Filtrer par mois si spécifié
    if months:
        if not df_expenses.empty:
            df_expenses = df_expenses[df_expenses['Mois'].isin(months)]
        if not df_revenues.empty:
            df_revenues = df_revenues[df_revenues['Mois'].isin(months)]
    
    total_expenses = df_expenses['Montant'].sum() if not df_expenses.empty else 0
    total_revenues = df_revenues['Montant'].sum() if not df_revenues.empty else 0
    balance = total_revenues - total_expenses
    
    return {
        'total_expenses': total_expenses,
        'total_revenues': total_revenues,
        'balance': balance,
        'savings_rate': (balance / total_revenues * 100) if total_revenues > 0 else 0
    }

def get_expenses_by_category(year, months=None):
    """Récupère les dépenses groupées par catégorie"""
    expenses = fetch_expenses()
    import pandas as pd
    
    df = pd.DataFrame(expenses)
    
    if df.empty:
        return {}
    
    df = df[df['Année'] == year]
    
    if months:
        df = df[df['Mois'].isin(months)]
    
    category_totals = df.groupby('Catégories')['Montant'].sum().to_dict()
    
    return category_totals

def get_monthly_data(year):
    """Récupère les données mensuelles pour une année"""
    expenses = fetch_expenses()
    revenues = fetch_revenues()
    
    import pandas as pd
    
    df_expenses = pd.DataFrame(expenses)
    df_revenues = pd.DataFrame(revenues)
    
    MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    monthly_expenses = {}
    monthly_revenues = {}
    
    if not df_expenses.empty:
        df_expenses = df_expenses[df_expenses['Année'] == year]
        monthly_expenses = df_expenses.groupby('Mois')['Montant'].sum().reindex(MOIS, fill_value=0).to_dict()
    
    if not df_revenues.empty:
        df_revenues = df_revenues[df_revenues['Année'] == year]
        monthly_revenues = df_revenues.groupby('Mois')['Montant'].sum().reindex(MOIS, fill_value=0).to_dict()
    
    return {
        'expenses': monthly_expenses,
        'revenues': monthly_revenues
    }
