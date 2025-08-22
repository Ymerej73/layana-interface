# 🔐 Système d'Authentification Layana

## 📋 Vue d'ensemble

Le système d'authentification Layana utilise **Supabase Auth** avec un système de **codes de rôle** pour contrôler l'accès et les permissions des utilisateurs.

## 🎯 Fonctionnalités

### ✅ **Inscription Sécurisée**
- Formulaire complet : Prénom, Nom, Email, Mot de passe
- **Codes de rôle** pour contrôler les permissions
- Validation côté client et serveur
- Métadonnées utilisateur enrichies

### ✅ **Connexion Sécurisée**
- Authentification par email/mot de passe
- Sessions sécurisées avec Flask
- Affichage du nom complet et du rôle
- Déconnexion sécurisée

### ✅ **Protection des Routes**
- Toutes les pages protégées (sauf `/login` et `/register`)
- Redirection automatique vers la page de connexion
- Gestion des sessions expirées

## 🔑 Codes de Rôle

| Code | Rôle | Description |
|------|------|-------------|
| `ADMIN2025` | **Administrateur** | Accès complet à toutes les fonctionnalités |
| `MANAGER2025` | **Manager Général** | Accès aux données clients et réservations |
| `RECEPTION2025` | **Réception** | Accès limité aux données de réception |
| `STAFF2025` | **Personnel** | Accès basique aux informations |

## 🚀 Utilisation

### **1. Inscription d'un Nouvel Utilisateur**

#### **Via l'Interface Web**
1. Aller sur `http://localhost:5003/register`
2. Remplir le formulaire :
   - **Prénom** : Prénom de l'utilisateur
   - **Nom** : Nom de l'utilisateur
   - **Email** : Adresse email professionnelle
   - **Mot de passe** : Minimum 8 caractères
   - **Code de rôle** : Code correspondant au rôle (ex: `ADMIN2025`)

#### **Via le Script Python**
```bash
python create_team_users_final.py
```

### **2. Connexion**
1. Aller sur `http://localhost:5003/login`
2. Saisir email et mot de passe
3. Redirection automatique vers le dashboard

### **3. Gestion des Sessions**
- **Affichage** : Nom complet et rôle dans le header
- **Déconnexion** : Bouton dans le menu utilisateur
- **Sécurité** : Sessions automatiquement expirées

## 📁 Structure des Fichiers

```
Layana_INTERFACE/
├── templates/
│   ├── login.html          # Page de connexion
│   ├── register.html       # Page d'inscription
│   └── base.html          # Template avec menu utilisateur
├── static/css/style.css   # Styles pour l'authentification
├── app.py                 # Routes et logique d'auth
├── create_team_users_final.py  # Script de création d'utilisateurs
└── SYSTEME_AUTHENTIFICATION.md # Ce guide
```

## 🔧 Configuration

### **Variables d'Environnement**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
```

### **Métadonnées Utilisateur**
Chaque utilisateur a les métadonnées suivantes :
```json
{
  "first_name": "Prénom",
  "last_name": "Nom",
  "full_name": "Prénom Nom",
  "role": "Nom du Rôle",
  "role_code": "CODE2025"
}
```

## 🛡️ Sécurité

### **Protection Implémentée**
- ✅ Validation des tokens JWT
- ✅ Sessions sécurisées Flask
- ✅ Protection CSRF implicite
- ✅ Validation côté client et serveur
- ✅ Codes de rôle obligatoires

### **Bonnes Pratiques**
- 🔒 **Codes de rôle confidentiels** : Ne pas partager les codes
- 🔒 **Mots de passe forts** : Minimum 8 caractères
- 🔒 **Emails professionnels** : Utiliser des emails @layana.com
- 🔒 **Déconnexion** : Toujours se déconnecter après utilisation

## 👥 Utilisateurs de l'Équipe

### **Administrateurs**
- **Jérémy CAUDAN** : `jeremy.caudan@layana.com` (ADMIN2025)
- **Isidore ZONGO** : `isidore.zongo@layana.com` (ADMIN2025)

### **Manager Général**
- **Franck DELEN** : `franck.delen@layana.com` (MANAGER2025)

### **Mot de passe par défaut**
- **Tous les utilisateurs** : `Layana2025!`

## 🔄 Workflow d'Inscription

1. **Accès à la page** : `/register`
2. **Saisie des informations** : Formulaire complet
3. **Validation** : Vérification des champs et du code de rôle
4. **Création** : Inscription via Supabase Auth
5. **Confirmation** : Message de succès
6. **Redirection** : Vers la page de connexion

## 🚨 Dépannage

### **Erreur "Database error saving new user"**
- **Cause** : Problème de configuration Supabase
- **Solution** : Vérifier les politiques RLS ou créer manuellement dans le dashboard

### **Erreur "Code de rôle invalide"**
- **Cause** : Code incorrect ou non autorisé
- **Solution** : Vérifier les codes disponibles dans l'interface

### **Erreur "Email déjà utilisé"**
- **Cause** : Compte existant
- **Solution** : Utiliser un autre email ou se connecter avec l'existant

### **Problème de connexion**
- **Cause** : Email non confirmé
- **Solution** : Confirmer l'email dans le dashboard Supabase

## 📞 Support

Pour toute question ou problème :
1. Vérifier ce guide
2. Consulter les logs de l'application
3. Vérifier la configuration Supabase
4. Tester avec un utilisateur de test

---

**🎉 Le système d'authentification Layana est maintenant opérationnel !**
