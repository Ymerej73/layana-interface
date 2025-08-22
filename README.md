# 🏨 Interface Layana - Gestion Hôtelière

Interface web moderne pour la gestion des clients et réservations de l'hôtel Layana.

## ✨ Fonctionnalités

### 🔐 **Authentification Sécurisée**
- **Connexion Supabase** : Authentification par email/mot de passe
- **Protection des routes** : Toutes les pages sont sécurisées
- **Sessions sécurisées** : Gestion des sessions avec Flask
- **Déconnexion** : Bouton de déconnexion dans le header

### 📊 **Tableau de bord**
- **Statistiques en temps réel** : Clients actuels, réservations en cours, futures et terminées
- **Message d'accueil personnalisé** : Bonjour/Bon après-midi/Bonsoir selon l'heure
- **Calendrier interactif** : Visualisation des arrivées (+) et départs (-) par jour
- **Navigation entre les mois** : Boutons précédent/suivant fonctionnels
- **Modal détaillée** : Clic sur un jour pour voir les clients arrivant/partant

### 👥 **Gestion des clients**
- **Liste complète** : Tous les clients avec informations détaillées
- **Recherche avancée** : Par nom, prénom, ID client, email, téléphone
- **Édition rapide** : Modification directe des emails et téléphones
- **Statuts** : En cours, futur, terminé, annulé
- **Détails complets** : Préférences alimentaires, chambre, services, transport

### 📅 **Gestion des réservations**
- **Liste complète** : Toutes les réservations avec détails
- **Recherche avancée** : Par ID réservation, chambre, nom client
- **Statuts** : En cours, futur, terminé, annulé
- **Informations détaillées** : Dates, chambres, clients principaux/secondaires

### 🎨 **Interface utilisateur**
- **Design moderne** : Thème doré (#C8A76B) et noir profond (#0E0E10)
- **Mode sombre/clair** : Basculement automatique avec préférence sauvegardée
- **Responsive** : Adaptation mobile et tablette
- **Navigation intuitive** : Barre de navigation avec date en français
- **Notifications** : Messages de confirmation et d'erreur

## 🚀 Installation

### Prérequis
- Python 3.8+
- Compte Supabase

### Configuration
1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd Layana_INTERFACE
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration Supabase**
   - Copier `config.env.example` vers `config.env`
   - Remplir les variables d'environnement :
     ```
     SUPABASE_URL=votre_url_supabase
     SUPABASE_KEY=votre_clé_service_role
     SUPABASE_ANON_KEY=votre_clé_anon
     ```
   - **Important** : Consultez `AUTHENTICATION_SETUP.md` pour la configuration complète de l'authentification

5. **Base de données**
   - Exécuter le script `database/schema.sql` dans l'éditeur SQL de Supabase
   - Créer les tables `clients` et `reservations`

6. **Créer un utilisateur de test**
   ```bash
   python create_test_user.py
   ```
   - Suivez les instructions pour créer un utilisateur de test
   - Ou créez manuellement un utilisateur dans le dashboard Supabase

## 🏃‍♂️ Démarrage

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python app.py
```

L'application sera accessible sur `http://localhost:5003`

**Note** : Vous serez redirigé vers la page de connexion si vous n'êtes pas authentifié.

## 📁 Structure du projet

```
Layana_INTERFACE/
├── app.py                 # Application Flask principale
├── config.env             # Variables d'environnement (à créer)
├── config.env.example     # Exemple de configuration
├── requirements.txt       # Dépendances Python
├── .gitignore            # Fichiers à ignorer par Git
├── README.md             # Documentation
├── static/               # Fichiers statiques
│   ├── css/
│   │   └── style.css     # Styles CSS
│   ├── js/
│   │   └── main.js       # JavaScript principal
│   └── images/           # Images
├── templates/            # Templates HTML
│   ├── login.html        # Page de connexion
│   └── ...               # Autres templates
├── create_test_user.py   # Script de création d'utilisateur
├── AUTHENTICATION_SETUP.md # Guide de configuration auth
│   ├── base.html         # Template de base
│   ├── dashboard.html    # Page d'accueil
│   ├── clients.html      # Gestion des clients
│   ├── reservations.html # Gestion des réservations
│   └── client_detail.html # Détail d'un client
└── venv/                 # Environnement virtuel
```

## 🗄️ Base de données

### Table `clients`
- `id` : Identifiant unique (auto-généré)
- `guest_name_id` : ID Opera du client
- `guest_name` : Nom complet
- `title` : Titre (M., Mme, etc.)
- `dietary_preferences` : Préférences alimentaires
- `room_preferences` : Préférences de chambre
- `service_preferences` : Préférences de services
- `transport_preferences` : Préférences de transport
- `status` : Statut (en_cours, futur, terminé, annulé)

### Table `reservations`
- `resv_name_id` : ID Opera de la réservation
- `arrival` : Date d'arrivée
- `departure` : Date de départ
- `room_no` : Numéro de chambre
- `client_principal_id` : ID du client principal
- `client_secondaire_id` : ID du client secondaire (optionnel)
- `status` : Statut (en_cours, futur, terminé, annulé)

## 🎯 Fonctionnalités techniques

### **Performance**
- **Cache intelligent** : Mise en cache des données avec timeout de 30 secondes
- **Requêtes optimisées** : Batch queries pour réduire les appels à Supabase
- **Debouncing** : Recherche avec délai de 1000ms pour éviter les requêtes excessives

### **Sécurité**
- **Variables d'environnement** : Clés sensibles dans config.env
- **Validation des données** : Vérification des entrées utilisateur
- **Gestion d'erreurs** : Messages d'erreur informatifs

### **UX/UI**
- **Thème cohérent** : Palette de couleurs Layana (or, noir, perle)
- **Responsive design** : Adaptation à tous les écrans
- **Accessibilité** : Navigation clavier et lecteurs d'écran
- **Feedback utilisateur** : Notifications et confirmations

## 🔧 API Endpoints

### **Pages principales**
- `GET /` : Tableau de bord
- `GET /clients` : Liste des clients
- `GET /reservations` : Liste des réservations
- `GET /client/<id>` : Détail d'un client

### **API REST**
- `GET /api/calendar/<year>/<month>` : Données du calendrier
- `PUT /api/client/<id>` : Modification d'un client
- `PUT /api/reservation/<id>` : Modification d'une réservation

## 🎨 Thème et design

### **Palette de couleurs**
- **Or principal** : #C8A76B
- **Noir profond** : #0E0E10
- **Perle** : #FFFAF3
- **Surface sombre** : #151517

### **Mode sombre**
- Arrière-plan : #0E0E10
- Surface : #151517
- Texte : Blanc
- Accents : Or

### **Mode clair**
- Arrière-plan : #FFFAF3
- Surface : #FFFAF3
- Texte : #000000
- Accents : Or

## 📱 Compatibilité

- **Navigateurs** : Chrome, Firefox, Safari, Edge (versions récentes)
- **Mobiles** : iOS Safari, Chrome Mobile
- **Tablettes** : iPad, Android tablets
- **Résolutions** : 320px à 4K

## 🚀 Déploiement

### **Production**
1. Configurer les variables d'environnement de production
2. Utiliser un serveur WSGI (Gunicorn, uWSGI)
3. Configurer un reverse proxy (Nginx)
4. Activer HTTPS avec certificat SSL

### **Docker** (optionnel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5003
CMD ["python", "app.py"]
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contacter l'équipe de développement

---

**Développé avec ❤️ pour l'hôtel Layana**
