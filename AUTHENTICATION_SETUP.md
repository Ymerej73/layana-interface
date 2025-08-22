# Configuration de l'Authentification Supabase

## Prérequis

1. Un projet Supabase actif
2. Les clés API Supabase (Service Role et Anon)

## Étapes de Configuration

### 1. Configuration des Variables d'Environnement

Modifiez votre fichier `config.env` avec les bonnes valeurs :

```env
# Configuration Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_service_role_key_here
SUPABASE_ANON_KEY=your_anon_key_here

# Configuration locale
DATA_PATH=./data
```

### 2. Configuration de l'Authentification dans Supabase

#### A. Activer l'Authentification par Email

1. Allez dans votre dashboard Supabase
2. Naviguez vers **Authentication** > **Settings**
3. Activez **Enable email confirmations** si vous voulez que les utilisateurs confirment leur email
4. Configurez les **Site URL** avec votre URL de production

#### B. Créer un Utilisateur de Test

1. Allez dans **Authentication** > **Users**
2. Cliquez sur **Add user**
3. Entrez un email et un mot de passe
4. L'utilisateur sera créé et pourra se connecter

#### C. Configuration des Politiques de Sécurité (Optionnel)

Si vous voulez restreindre l'accès aux données selon les utilisateurs :

```sql
-- Exemple de politique pour la table clients
CREATE POLICY "Users can view clients" ON clients
FOR SELECT USING (auth.role() = 'authenticated');

-- Exemple de politique pour la table reservations
CREATE POLICY "Users can view reservations" ON reservations
FOR SELECT USING (auth.role() = 'authenticated');
```

### 3. Test de l'Authentification

1. Démarrez l'application : `python app.py`
2. Allez sur `http://localhost:5003/login`
3. Connectez-vous avec les identifiants créés
4. Vous devriez être redirigé vers le dashboard

## Fonctionnalités Implémentées

### ✅ Authentification Sécurisée
- Connexion avec email/mot de passe via Supabase Auth
- Validation des tokens JWT côté serveur
- Sessions sécurisées avec Flask

### ✅ Protection des Routes
- Toutes les pages sont protégées (sauf `/login`)
- Redirection automatique vers la page de connexion
- Déconnexion sécurisée

### ✅ Interface Utilisateur
- Page de connexion moderne avec les couleurs Layana
- Gestion des erreurs de connexion
- Bouton de déconnexion dans le header
- Affichage de l'email de l'utilisateur connecté

### ✅ Sécurité
- Validation des tokens côté client et serveur
- Sessions sécurisées
- Protection CSRF implicite avec Flask

## Dépannage

### Erreur "Token invalide"
- Vérifiez que `SUPABASE_ANON_KEY` est correcte
- Assurez-vous que l'authentification est activée dans Supabase

### Erreur "Email ou mot de passe incorrect"
- Vérifiez que l'utilisateur existe dans Supabase
- Assurez-vous que l'email est confirmé si nécessaire

### Erreur de connexion à Supabase
- Vérifiez `SUPABASE_URL` et `SUPABASE_KEY`
- Assurez-vous que votre projet Supabase est actif

## Notes de Sécurité

1. **Ne partagez jamais** votre `SUPABASE_KEY` (Service Role)
2. La `SUPABASE_ANON_KEY` peut être exposée côté client
3. Les tokens JWT ont une durée de vie limitée
4. Les sessions Flask sont sécurisées par défaut

## Prochaines Étapes (Optionnel)

1. **Gestion des Rôles** : Ajouter des rôles utilisateur (admin, réception, etc.)
2. **Récupération de mot de passe** : Implémenter la réinitialisation
3. **Authentification à deux facteurs** : Ajouter la 2FA
4. **Audit des connexions** : Logger les tentatives de connexion
