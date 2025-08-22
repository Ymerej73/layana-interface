#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test dans Supabase
Utilisez ce script pour créer un utilisateur de test pour l'authentification
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('config.env')

# Configuration Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Erreur: SUPABASE_URL et SUPABASE_KEY doivent être définis dans config.env")
    exit(1)

# Créer le client Supabase
supabase: Client = create_client(supabase_url, supabase_key)

def create_test_user():
    """Créer un utilisateur de test"""
    try:
        # Informations de l'utilisateur de test
        email = "admin@layana.com"
        password = "Layana2025!"
        
        print(f"🔐 Création de l'utilisateur de test...")
        print(f"📧 Email: {email}")
        print(f"🔑 Mot de passe: {password}")
        print()
        
        # Créer l'utilisateur
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True  # Confirmer automatiquement l'email
        })
        
        if response.user:
            print("✅ Utilisateur créé avec succès!")
            print(f"🆔 ID utilisateur: {response.user.id}")
            print(f"📧 Email: {response.user.email}")
            print()
            print("🎉 Vous pouvez maintenant vous connecter avec:")
            print(f"   Email: {email}")
            print(f"   Mot de passe: {password}")
            print()
            print("🌐 Allez sur: http://localhost:5003/login")
            
        else:
            print("❌ Erreur lors de la création de l'utilisateur")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        
        # Si l'utilisateur existe déjà
        if "User already registered" in str(e):
            print()
            print("ℹ️  L'utilisateur existe déjà. Vous pouvez vous connecter avec:")
            print(f"   Email: {email}")
            print(f"   Mot de passe: {password}")
            print()
            print("🌐 Allez sur: http://localhost:5003/login")

def create_team_users():
    """Créer les utilisateurs de l'équipe Layana"""
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
    
    print("👥 Création des utilisateurs de l'équipe Layana")
    print("=" * 60)
    print()
    
    created_users = []
    existing_users = []
    
    for user in users:
        try:
            print(f"🔐 Création de {user['name']} ({user['role']})...")
            print(f"📧 Email: {user['email']}")
            print(f"🔑 Mot de passe: {user['password']}")
            
            # Créer l'utilisateur
            response = supabase.auth.admin.create_user({
                "email": user['email'],
                "password": user['password'],
                "email_confirm": True,
                "user_metadata": {
                    "name": user['name'],
                    "role": user['role']
                }
            })
            
            if response.user:
                print("✅ Utilisateur créé avec succès!")
                print(f"🆔 ID: {response.user.id}")
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

def list_users():
    """Lister tous les utilisateurs"""
    try:
        print("👥 Liste des utilisateurs:")
        print("-" * 50)
        
        response = supabase.auth.admin.list_users()
        
        for user in response.users:
            print(f"🆔 ID: {user.id}")
            print(f"📧 Email: {user.email}")
            print(f"✅ Confirmé: {user.email_confirmed_at is not None}")
            print(f"📅 Créé le: {user.created_at}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des utilisateurs: {str(e)}")

if __name__ == "__main__":
    print("🚀 Script de gestion des utilisateurs Supabase")
    print("=" * 50)
    print()
    
    # Demander l'action à effectuer
    action = input("Que voulez-vous faire?\n1. Créer un utilisateur de test\n2. Créer les utilisateurs de l'équipe Layana\n3. Lister les utilisateurs\nVotre choix (1, 2 ou 3): ").strip()
    
    if action == "1":
        create_test_user()
    elif action == "2":
        create_team_users()
    elif action == "3":
        list_users()
    else:
        print("❌ Choix invalide. Utilisez 1, 2 ou 3.")
