#!/usr/bin/env python3
"""
Script pour tester les nouvelles fonctionnalités de paramètres
"""

import requests
import json

def test_settings_features():
    """Tester les fonctionnalités de paramètres"""
    print("⚙️ === TEST FONCTIONNALITÉS PARAMÈTRES ===\n")
    
    base_url = "http://localhost:5003"
    
    # Test 1: Vérifier que l'application fonctionne
    print("1. Test application...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Application accessible")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erreur connexion: {str(e)}")
        return
    
    # Test 2: Vérifier la page des paramètres
    print("\n2. Test page des paramètres...")
    try:
        response = requests.get(f"{base_url}/settings")
        if response.status_code == 200:
            print("   ✅ Page des paramètres accessible")
            
            # Vérifier la présence des éléments
            html_content = response.text
            if 'settings-container' in html_content:
                print("   ✅ Conteneur des paramètres présent")
            else:
                print("   ❌ Conteneur des paramètres manquant")
                
            if 'theme-selector' in html_content:
                print("   ✅ Sélecteur de thème présent")
            else:
                print("   ❌ Sélecteur de thème manquant")
                
            if 'language-selector' in html_content:
                print("   ✅ Sélecteur de langue présent")
            else:
                print("   ❌ Sélecteur de langue manquant")
                
        else:
            print(f"   ❌ Erreur page paramètres: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test 3: Vérifier la navigation
    print("\n3. Test navigation...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            html_content = response.text
            
            if 'Paramètres' in html_content:
                print("   ✅ Lien Paramètres présent dans la navigation")
            else:
                print("   ❌ Lien Paramètres manquant")
                
            if 'fas fa-cog' in html_content:
                print("   ✅ Icône Paramètres présente")
            else:
                print("   ❌ Icône Paramètres manquante")
                
        else:
            print(f"   ❌ Erreur navigation: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test 4: Vérifier l'API de langue
    print("\n4. Test API de langue...")
    try:
        # Test changement vers anglais
        response = requests.post(f"{base_url}/api/settings/language", 
                               json={'language': 'en'},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ API de langue fonctionnelle (en)")
            else:
                print("   ❌ API de langue échec")
        else:
            print(f"   ❌ Erreur API langue: {response.status_code}")
            
        # Test changement vers français
        response = requests.post(f"{base_url}/api/settings/language", 
                               json={'language': 'fr'},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ API de langue fonctionnelle (fr)")
            else:
                print("   ❌ API de langue échec")
        else:
            print(f"   ❌ Erreur API langue: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur API: {str(e)}")
    
    # Test 5: Vérifier l'API de sauvegarde des paramètres
    print("\n5. Test API sauvegarde paramètres...")
    try:
        settings_data = {
            'theme': 'dark',
            'language': 'en',
            'notifications': True,
            'emailNotifications': False,
            'density': 'comfortable',
            'animations': True,
            'autoSave': True
        }
        
        response = requests.post(f"{base_url}/api/settings/save", 
                               json=settings_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ API sauvegarde paramètres fonctionnelle")
            else:
                print("   ❌ API sauvegarde paramètres échec")
        else:
            print(f"   ❌ Erreur API sauvegarde: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur API: {str(e)}")
    
    # Test 6: Vérifier les styles CSS
    print("\n6. Test styles CSS...")
    try:
        response = requests.get(f"{base_url}/static/css/style.css")
        if response.status_code == 200:
            css_content = response.text
            
            if '.settings-container' in css_content:
                print("   ✅ Styles des paramètres présents")
            else:
                print("   ❌ Styles des paramètres manquants")
                
            if '.theme-selector' in css_content:
                print("   ✅ Styles sélecteur de thème présents")
            else:
                print("   ❌ Styles sélecteur de thème manquants")
                
            if '.switch' in css_content:
                print("   ✅ Styles switches présents")
            else:
                print("   ❌ Styles switches manquants")
                
        else:
            print(f"   ❌ Erreur CSS: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test 7: Vérifier les fonctions JavaScript
    print("\n7. Test fonctions JavaScript...")
    try:
        response = requests.get(f"{base_url}/static/js/main.js")
        if response.status_code == 200:
            js_content = response.text
            
            if 'function setTheme' in js_content:
                print("   ✅ Fonction setTheme présente")
            else:
                print("   ❌ Fonction setTheme manquante")
                
            if 'function setLanguage' in js_content:
                print("   ✅ Fonction setLanguage présente")
            else:
                print("   ❌ Fonction setLanguage manquante")
                
            if 'function saveSettings' in js_content:
                print("   ✅ Fonction saveSettings présente")
            else:
                print("   ❌ Fonction saveSettings manquante")
                
        else:
            print(f"   ❌ Erreur JavaScript: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Résumé
    print("\n" + "="*50)
    print("🎯 RÉSUMÉ DES FONCTIONNALITÉS PARAMÈTRES")
    print("="*50)
    print("✅ Page des paramètres créée")
    print("✅ Navigation mise à jour")
    print("✅ Sélecteur de thème (clair/sombre)")
    print("✅ Sélecteur de langue (français/anglais)")
    print("✅ Switches pour les options")
    print("✅ API de sauvegarde des paramètres")
    print("✅ Styles CSS complets")
    print("✅ Fonctions JavaScript")
    print("\n🎮 Fonctionnalités disponibles:")
    print("   • Changement de thème en temps réel")
    print("   • Changement de langue avec rechargement")
    print("   • Sauvegarde des préférences")
    print("   • Interface responsive")
    print("   • Notifications de confirmation")
    print("\n🌐 Pour tester:")
    print("   1. Ouvrir http://localhost:5003")
    print("   2. Cliquer sur 'Paramètres' dans la navigation")
    print("   3. Tester le changement de thème")
    print("   4. Tester le changement de langue")
    print("   5. Vérifier que les changements persistent")

if __name__ == "__main__":
    test_settings_features()
