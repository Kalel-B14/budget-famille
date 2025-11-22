[PARAMETRES_GUIDE.md](https://github.com/user-attachments/files/23691680/PARAMETRES_GUIDE.md)
# 🎨 Module Paramètres - Guide Complet

## ✨ Fonctionnalités Implémentées

### 1. 👤 **Gestion du Profil**
- ✅ Upload de photo de profil
- ✅ Prévisualisation avant enregistrement
- ✅ Affichage de la photo sur toutes les pages
- ✅ Format supporté: PNG, JPG, JPEG
- ✅ Stockage en base64 dans Firebase

### 2. 👥 **Gestion des Utilisateurs**
- ✅ Affichage de tous les utilisateurs avec leurs photos
- ✅ Ajout de nouveaux utilisateurs
- ✅ Suppression d'utilisateurs (minimum 2 utilisateurs)
- ✅ Les nouveaux utilisateurs apparaissent automatiquement à la connexion
- ✅ Chaque utilisateur a sa propre session

### 3. 🏠 **Paramètres Famille**
- ✅ Modification du nom de famille
- ✅ Affichage dynamique sur la page d'accueil
- ✅ Sauvegarde dans Firebase

### 4. 💰 **Paramètres Budget**
- ✅ Gestion des catégories de dépenses
  - Ajout de nouvelles catégories
  - Suppression de catégories (sauf "Autre")
  - Affichage en liste
- ✅ Gestion des sources de revenus
  - Ajout de nouvelles sources
  - Suppression de sources (sauf "Autre")
  - Affichage en liste

### 5. 🎨 **Personnalisation du Thème**
- ✅ Mode sombre / clair
- ✅ 5 palettes de couleurs:
  - 🟣 Violet (défaut)
  - 🔵 Bleu
  - 🟢 Vert
  - 🌸 Rose
  - 🔴 Rouge
- ✅ Prévisualisation en temps réel
- ✅ Sauvegarde par utilisateur
- ✅ Application automatique au rechargement

## 📁 Fichiers Créés

```
services/
└── parametres_service.py    ← Nouvelle logique métier

pages/
└── Parametres.py            ← Nouvelle page

streamlit_app.py             ← Modifié (utilisateurs dynamiques + nom famille)
```

## 🔥 Structure Firebase

### Collections Ajoutées

```
config/
├── users                    # Liste des utilisateurs
│   └── list: [array]
├── family                   # Nom de famille
│   └── name: string
└── budget                   # Configuration budget
    ├── expense_categories: [array]
    └── revenue_sources: [array]

user_themes/
├── Margaux
│   ├── mode: "dark"/"light"
│   └── palette: "Violet"/"Bleu"/etc.
└── Souliman
    ├── mode: "dark"/"light"
    └── palette: "Violet"/"Bleu"/etc.

user_profiles/
├── Margaux
│   ├── profile_image: base64
│   └── created_at: timestamp
└── Souliman
    ├── profile_image: base64
    └── created_at: timestamp
```

## 🎯 Utilisation

### Accès aux Paramètres

1. **Depuis la page d'accueil** : Cliquez sur le bouton **⚙️ Paramètres** en haut à droite
2. **Depuis n'importe quelle page** : Le bandeau utilisateur avec ⚙️ est toujours présent

### Modifier sa Photo de Profil

1. Aller dans **⚙️ Paramètres** → **👤 Profil**
2. Cliquer sur "Choisir une nouvelle photo"
3. Sélectionner une image (PNG, JPG, JPEG)
4. Prévisualiser
5. Cliquer sur **💾 Enregistrer cette photo**
6. ✅ La photo apparaît instantanément partout

### Ajouter un Utilisateur

1. Aller dans **⚙️ Paramètres** → **👥 Utilisateurs**
2. Descendre jusqu'à "Ajouter un nouvel utilisateur"
3. Entrer le nom (ex: "Papa", "Maman", "Lucas")
4. Cliquer sur **➕ Ajouter l'utilisateur**
5. ✅ L'utilisateur apparaît sur la page de connexion

### Modifier le Nom de Famille

1. Aller dans **⚙️ Paramètres** → **🏠 Famille**
2. Modifier le nom dans le champ
3. Cliquer sur **💾 Enregistrer**
4. ✅ Le nom change sur la page d'accueil

### Personnaliser les Catégories Budget

1. Aller dans **⚙️ Paramètres** → **💰 Budget**
2. **Pour ajouter une catégorie** :
   - Colonne de gauche (Dépenses) ou droite (Revenus)
   - Entrer le nom dans le champ
   - Cliquer sur **➕ Ajouter**
3. **Pour supprimer** :
   - Cliquer sur 🗑️ à côté de la catégorie

### Changer le Thème

1. Aller dans **⚙️ Paramètres** → **🎨 Thème**
2. Choisir le mode (🌙 Sombre / ☀️ Clair)
3. Choisir une palette de couleurs
4. Voir la prévisualisation
5. Cliquer sur **💾 Appliquer ce thème**
6. ✅ La page se recharge avec le nouveau thème

## 🎨 Palettes Disponibles

### 🟣 Violet (Défaut)
- Primary: `#667eea`
- Secondary: `#764ba2`
- Gradient moderne et professionnel

### 🔵 Bleu
- Primary: `#4299e1`
- Secondary: `#3182ce`
- Calme et apaisant

### 🟢 Vert
- Primary: `#48bb78`
- Secondary: `#38a169`
- Nature et fraîcheur

### 🌸 Rose
- Primary: `#ed64a6`
- Secondary: `#d53f8c`
- Doux et chaleureux

### 🔴 Rouge
- Primary: `#f56565`
- Secondary: `#e53e3e`
- Dynamique et énergique

## 💡 Points Importants

### Sécurité
- ✅ Minimum 2 utilisateurs toujours présents
- ✅ Impossible de supprimer "Autre" dans les catégories
- ✅ Thème personnel : chaque utilisateur a son propre thème

### Performance
- ✅ Images stockées en base64 (optimisé pour petit fichiers)
- ✅ Chargement paresseux des données
- ✅ Cache Firebase intégré

### Limites
- 📷 Taille d'image recommandée : < 1MB
- 👥 Nombre d'utilisateurs recommandé : < 10
- 📝 Nombre de catégories recommandé : < 50

## 🔄 Prochaines Améliorations

### Futures Fonctionnalités
- [ ] Compression automatique des images
- [ ] Réorganisation des catégories par drag & drop
- [ ] Thèmes personnalisés (choix de couleurs manuelles)
- [ ] Export/Import de configuration
- [ ] Gestion des permissions par utilisateur

## 📦 Déploiement

### Fichiers à Commiter

```bash
git add services/parametres_service.py
git add pages/Parametres.py
git add streamlit_app.py
git commit -m "feat: Module Paramètres complet avec thèmes et gestion utilisateurs"
git push
```

### Test Local

```bash
streamlit run streamlit_app.py
```

### Vérifications Après Déploiement

1. ✅ Connexion fonctionne avec tous les utilisateurs
2. ✅ Upload de photo fonctionne
3. ✅ Photos s'affichent partout
4. ✅ Ajout/suppression utilisateurs
5. ✅ Modification nom de famille
6. ✅ Gestion catégories budget
7. ✅ Changement de thème avec application immédiate

## 🐛 Dépannage

### "Firebase non disponible"
➡️ Vérifiez `.streamlit/secrets.toml`

### "Photo ne s'affiche pas"
➡️ Vérifiez la taille (< 5MB) et le format (PNG/JPG)

### "Utilisateur ne s'affiche pas à la connexion"
➡️ Rafraîchissez la page (Ctrl+F5)

### "Thème ne change pas"
➡️ Rechargez complètement la page après sauvegarde

---

## 🎉 Félicitations !

Votre module Paramètres est maintenant **complet et fonctionnel** ! 

Tous les paramètres sont **personnalisés par utilisateur** et **sauvegardés dans Firebase**.

Profitez de votre application Famileasy personnalisée ! 🏠✨
