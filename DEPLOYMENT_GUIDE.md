# 🚀 Guide de Déploiement - Interface Layana

## 📋 Prérequis

1. **Compte GitHub** avec votre code source
2. **Compte Supabase** configuré
3. **Variables d'environnement** prêtes

## 🔧 Configuration des Variables d'Environnement

Créez un fichier `config.env` avec ces variables :

```env
# Supabase Configuration
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_service_role_key
SUPABASE_ANON_KEY=votre_anon_key

# Flask Configuration
SECRET_KEY=votre_secret_key_tres_securise

# Configuration locale
DATA_PATH=./data
```

## 🌐 Option 1: Déploiement sur Render.com (Recommandé)

### Étape 1: Préparer le Repository
```bash
# Créer un repository GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/votre-username/layana-interface.git
git push -u origin main
```

### Étape 2: Configurer Render
1. Allez sur [render.com](https://render.com)
2. Créez un compte et connectez-vous
3. Cliquez sur "New +" → "Web Service"
4. Connectez votre repository GitHub
5. Configurez le service :
   - **Name** : `layana-interface`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`

### Étape 3: Variables d'Environnement sur Render
Dans les paramètres du service, ajoutez ces variables :
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_ANON_KEY`
- `SECRET_KEY`
- `FLASK_ENV=production`

### Étape 4: Déployer
Cliquez sur "Create Web Service" et attendez le déploiement.

## 🚂 Option 2: Déploiement sur Railway.app

### Étape 1: Préparer le Repository
Même processus que Render.

### Étape 2: Configurer Railway
1. Allez sur [railway.app](https://railway.app)
2. Créez un compte et connectez-vous
3. Cliquez sur "New Project" → "Deploy from GitHub repo"
4. Sélectionnez votre repository

### Étape 3: Variables d'Environnement
Dans l'onglet "Variables", ajoutez les mêmes variables que pour Render.

### Étape 4: Déployer
Railway détecte automatiquement que c'est une app Python et la déploie.

## 🏗️ Option 3: Déploiement sur Heroku

### Étape 1: Installer Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# Ou téléchargez depuis heroku.com
```

### Étape 2: Préparer l'Application
```bash
# Login à Heroku
heroku login

# Créer l'app
heroku create layana-interface

# Ajouter les variables d'environnement
heroku config:set SUPABASE_URL=votre_url_supabase
heroku config:set SUPABASE_KEY=votre_service_role_key
heroku config:set SUPABASE_ANON_KEY=votre_anon_key
heroku config:set SECRET_KEY=votre_secret_key
heroku config:set FLASK_ENV=production

# Déployer
git push heroku main
```

## 🔒 Sécurité en Production

### 1. Variables d'Environnement
- **Ne jamais** commiter les vraies clés dans le code
- Utilisez toujours les variables d'environnement
- Changez la `SECRET_KEY` pour quelque chose de complexe

### 2. Configuration Supabase
- Vérifiez que RLS (Row Level Security) est activé
- Configurez les politiques de sécurité appropriées
- Utilisez la clé anonyme pour l'authentification côté client

### 3. HTTPS
- Tous les services recommandés fournissent HTTPS automatiquement
- Vérifiez que votre domaine utilise HTTPS

## 🧪 Test du Déploiement

### 1. Vérification de Base
- L'application se charge-t-elle ?
- La page de login s'affiche-t-elle ?
- L'authentification fonctionne-t-elle ?

### 2. Test des Fonctionnalités
- Connexion avec un utilisateur test
- Navigation entre les pages
- Fonctionnalités d'édition rapide
- Affichage des données

### 3. Logs et Monitoring
- Vérifiez les logs du service
- Surveillez les erreurs
- Testez les performances

## 🔧 Dépannage

### Erreur 500
- Vérifiez les variables d'environnement
- Consultez les logs du service
- Testez localement avec les mêmes variables

### Erreur de Connexion Supabase
- Vérifiez les clés Supabase
- Testez la connexion depuis l'interface Supabase
- Vérifiez les politiques RLS

### Problème d'Authentification
- Vérifiez la `SUPABASE_ANON_KEY`
- Testez l'authentification côté client
- Vérifiez les redirections

## 📞 Support

En cas de problème :
1. Consultez les logs du service de déploiement
2. Vérifiez la documentation du service choisi
3. Testez localement avec les mêmes variables
4. Contactez le support du service si nécessaire

## 🎯 Recommandation Finale

**Pour commencer** : Utilisez **Render.com** - c'est gratuit, simple et parfait pour tester.

**Pour la production** : Passez à **Railway.app** ou **Heroku** pour plus de stabilité.

Votre application Layana sera bientôt accessible partout dans le monde ! 🌍
