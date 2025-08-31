#!/usr/bin/env python3
"""
Script de test pour la logique de salutation
"""

from datetime import datetime

def test_greeting_logic():
    """Tester la logique de salutation selon l'heure"""
    
    # Simuler différentes heures
    test_hours = [5, 11, 17, 23]
    test_names = ["Jérémy", "John", ""]
    
    print("🧪 Test de la logique de salutation")
    print("=" * 40)
    
    for hour in test_hours:
        print(f"\n🕐 Heure: {hour:02d}:00")
        
        # Déterminer le message de base selon l'heure
        if 5 <= hour < 12:
            base_greeting_fr = "Bonjour"
            base_greeting_en = "Good morning"
        elif 12 <= hour < 18:
            base_greeting_fr = "Bon après-midi"
            base_greeting_en = "Good afternoon"
        else:
            base_greeting_fr = "Bonsoir"
            base_greeting_en = "Good evening"
        
        print(f"🇫🇷 Français: {base_greeting_fr}")
        print(f"🇬🇧 Anglais: {base_greeting_en}")
        
        # Tester avec différents prénoms
        for name in test_names:
            if name:
                greeting_fr = f"{base_greeting_fr} {name}"
                greeting_en = f"{base_greeting_en} {name}"
                print(f"   Avec prénom: {greeting_fr} / {greeting_en}")
            else:
                print(f"   Sans prénom: {base_greeting_fr} / {base_greeting_en}")
    
    print("\n✅ Test terminé!")
    print("\n📝 Résultat attendu:")
    print("- 5h-11h: Bonjour/Good morning")
    print("- 12h-17h: Bon après-midi/Good afternoon") 
    print("- 18h-4h: Bonsoir/Good evening")
    print("- Prénom ajouté une seule fois")

if __name__ == "__main__":
    test_greeting_logic()
