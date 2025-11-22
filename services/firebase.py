import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

def init_firebase():
    """Initialise Firebase si ce n'est pas déjà fait"""
    if not firebase_admin._apps:
        firebase_secrets = st.secrets["firebase"]
        cred_dict = {
            "type": firebase_secrets["type"],
            "project_id": firebase_secrets["project_id"],
            "private_key_id": firebase_secrets["private_key_id"],
            "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),
            "client_email": firebase_secrets["client_email"],
            "client_id": firebase_secrets["client_id"],
            "auth_uri": firebase_secrets["auth_uri"],
            "token_uri": firebase_secrets["token_uri"],
            "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
        }
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

def get_user_profile(user):
    """Récupère le profil complet d'un utilisateur"""
    db = firestore.client()
    profile_ref = db.collection('user_profiles').document(user)
    doc = profile_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def save_user_profile(user, data):
    """Sauvegarde le profil utilisateur"""
    db = firestore.client()
    profile_ref = db.collection('user_profiles').document(user)
    data['last_update'] = time.time()
    profile_ref.set(data, merge=True)

def load_profile_image(user):
    """Charge l'image de profil d'un utilisateur"""
    profile = get_user_profile(user)
    if profile:
        return profile.get('profile_image')
    return None

def save_profile_image(user, image_data):
    """Sauvegarde l'image de profil"""
    save_user_profile(user, {'profile_image': image_data})

def add_notification(title, message, user, module="general"):
    """Ajoute une notification"""
    db = firestore.client()
    notif_ref = db.collection('notifications').document()
    notif_ref.set({
        'title': title,
        'message': message,
        'user': user,
        'module': module,
        'timestamp': time.time(),
        'read': False
    })

def get_notifications(limit=50):
    """Récupère les notifications récentes"""
    db = firestore.client()
    notifs_ref = db.collection('notifications').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
    docs = notifs_ref.stream()
    notifications = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        notifications.append(data)
    return notifications

def mark_notification_as_read(doc_id):
    """Marque une notification comme lue"""
    db = firestore.client()
    db.collection('notifications').document(doc_id).update({'read': True})

def get_unread_notifications_count():
    """Compte les notifications non lues"""
    db = firestore.client()
    notifs_ref = db.collection('notifications').where('read', '==', False)
    docs = list(notifs_ref.stream())
    return len(docs)

def save_user_preferences(user, preferences):
    """Sauvegarde les préférences utilisateur"""
    db = firestore.client()
    pref_ref = db.collection('user_preferences').document(user)
    preferences['last_update'] = time.time()
    pref_ref.set(preferences, merge=True)

def load_user_preferences(user):
    """Charge les préférences utilisateur"""
    db = firestore.client()
    pref_ref = db.collection('user_preferences').document(user)
    doc = pref_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None
