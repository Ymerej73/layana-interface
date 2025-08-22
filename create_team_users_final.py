#!/usr/bin/env python3
"""
Script pour créer les utilisateurs de l'équipe Layana avec les nouveaux codes de rôle
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

def create_team_users():
    """Créer les utilisateurs de l'équipe Layana avec les nouveaux codes de rôle"""
    users = [
        {
            "name": "Jérémy CAUDAN",
            "email": "jeremy.caudan@layana.com",
            "password": "Layana2025!",
            "role": "Administrateur",
            "role_code": "ADMIN2025"
        },
        {
            "name": "Isidore ZONGO", 
            "email": "isidore.zongo@layana.com",
            "password": "Layana2025!",
            "role": "Administrateur",
            "role_code": "ADMIN2025"
        },
        {
            "name": "Franck DELEN",
            "email": "franck.delen@layana.com", 
            "password": "Layana2025!",
            "role": "Manager Général",
            "role_code": "MANAGER2025"
        }
    ]
    
    print("👥 Création des utilisateurs de l'équipe Layana")
    print("=" * 60)
    print()
    print("📋 Codes de rôle utilisés:")
    print("   • ADMIN2025 - Administrateur")
    print("   • MANAGER2025 - Manager Général")
    print()
    
    created_users = []
    existing_users = []
    
    for user in users:
        try:
            print(f"🔐 Création de {user['name']} ({user['role']})...")
            print(f"📧 Email: {user['email']}")
            print(f"🔑 Mot de passe: {user['password']}")
            print(f"🎯 Code de rôle: {user['role_code']}")
            
            # Extraire prénom et nom
            name_parts = user['name'].split(' ')
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Créer l'utilisateur via l'API publique
            response = supabase.auth.sign_up({
                "email": user['email'],
                "password": user['password'],
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "full_name": user['name'],
                        "role": user['role'],
                        "role_code": user['role_code']
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
    print("   3. Confirmer manuellement les emails")
    print()
    print("🔐 Ou utilisez la page d'inscription:")
    print("   http://localhost:5003/register")

if __name__ == "__main__":
    print("🚀 Script de création des utilisateurs Layana")
    print("=" * 60)
    print()
    
    create_team_users()
