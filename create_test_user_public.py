#!/usr/bin/env python3
"""
Script alternatif pour créer des utilisateurs via l'API publique Supabase
Utilise l'API d'inscription au lieu de l'API admin
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('config.env')

# Configuration Supabase (utilise la clé anonyme pour l'inscription)
supabase_url = os.getenv('SUPABASE_URL')
supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_anon_key:
    print("❌ Erreur: SUPABASE_URL et SUPABASE_ANON_KEY doivent être définis dans config.env")
    exit(1)

# Créer le client Supabase avec la clé anonyme
supabase: Client = create_client(supabase_url, supabase_anon_key)

def create_team_users_public():
    """Créer les utilisateurs via l'API publique d'inscription"""
    users = [
        {
            "name": "Jérémy CAUDAN",
            "email": "jeremy.caudan@layana.com",
            "password": "Layana2025!",
            "role": "Administrateur"
        },
        {
            "name": "Isidore ZONGO", 
            "email": "isidore.zongo@layana.com",
            "password": "Layana2025!",
            "role": "Administrateur"
        },
        {
            "name": "Franck DELEN",
            "email": "franck.delen@layana.com", 
            "password": "Layana2025!",
            "role": "Manager Général Hôtel"
        }
    ]
    
    print("👥 Création des utilisateurs via l'API publique")
    print("=" * 60)
    print()
    print("⚠️  Note: Cette méthode nécessite que l'email soit confirmé manuellement")
    print("   ou que la confirmation d'email soit désactivée dans Supabase.")
    print()
    
    created_users = []
    existing_users = []
    
    for user in users:
        try:
            print(f"🔐 Création de {user['name']} ({user['role']})...")
            print(f"📧 Email: {user['email']}")
            print(f"🔑 Mot de passe: {user['password']}")
            
            # Créer l'utilisateur via l'API publique
            response = supabase.auth.sign_up({
                "email": user['email'],
                "password": user['password'],
                "options": {
                    "data": {
                        "name": user['name'],
                        "role": user['role']
                    }
                }
            })
            
            if response.user:
                print("✅ Utilisateur créé avec succès!")
                print(f"🆔 ID: {response.user.id}")
                print(f"📧 Email confirmé: {response.user.email_confirmed_at is not None}")
                created_users.append(user)
            else:
                print("❌ Erreur lors de la création")
                
        except Exception as e:
            if "User already registered" in str(e):
                print("ℹ️  Utilisateur existe déjà")
                existing_users.append(user)
            else:
                print(f"❌ Erreur: {str(e)}")
        
        print("-" * 40)
    
    # Résumé
    print()
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    if created_users:
        print("✅ Utilisateurs créés avec succès:")
        for user in created_users:
            print(f"   • {user['name']} ({user['role']}) - {user['email']}")
    
    if existing_users:
        print("ℹ️  Utilisateurs existants:")
        for user in existing_users:
            print(f"   • {user['name']} ({user['role']}) - {user['email']}")
    
    print()
    print("🎉 Tous les utilisateurs peuvent se connecter avec:")
    print("   Mot de passe: Layana2025!")
    print()
    print("🌐 Allez sur: http://localhost:5003/login")
    print()
    print("⚠️  Si les emails ne sont pas confirmés, vous devrez:")
    print("   1. Aller dans le dashboard Supabase")
    print("   2. Authentication > Users")
    print("   3. Confirer manuellement les emails")

if __name__ == "__main__":
    print("🚀 Script de création d'utilisateurs (API publique)")
    print("=" * 60)
    print()
    
    create_team_users_public()
