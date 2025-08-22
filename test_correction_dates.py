#!/usr/bin/env python3
"""
Script pour tester la correction des dates dans les clients actuels
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_reservations_actuelles, get_chambres_actuelles_from_reservations
from datetime import date

def test_correction_dates():
    """Tester la correction des dates"""
    print("📅 === TEST CORRECTION DATES CLIENTS ACTUELS ===\n")
    
    today = date.today()
    print(f"📅 Date actuelle: {today.isoformat()}")
    
    # Test 1: Récupérer les réservations actuelles
    print("\n1. Récupération des réservations actuelles...")
    try:
        reservations = get_reservations_actuelles()
        print(f"   ✅ {len(reservations)} réservations trouvées")
        
        if reservations:
            print("   📋 Vérification des dates de départ:")
            reservations_apres_aujourd_hui = 0
            reservations_avant_aujourd_hui = 0
            
            for res in reservations:
                departure_str = res.get('departure')
                if departure_str:
                    try:
                        if 'T' in departure_str:
                            departure = departure_str.split('T')[0]
                        else:
                            departure = departure_str
                        
                        departure_date = date.fromisoformat(departure)
                        
                        if departure_date >= today:
                            reservations_apres_aujourd_hui += 1
                        else:
                            reservations_avant_aujourd_hui += 1
                            print(f"      ⚠️ Réservation {res.get('resv_name_id')} part le {departure_date} (AVANT aujourd'hui!)")
                            print(f"         Chambre: {res.get('room_no')}, Statut: {res.get('statut')}")
                    except Exception as e:
                        print(f"      ❌ Erreur parsing date {departure_str}: {str(e)}")
            
            print(f"\n   📊 Résultats:")
            print(f"      ✅ Départs après aujourd'hui: {reservations_apres_aujourd_hui}")
            print(f"      ❌ Départs avant aujourd'hui: {reservations_avant_aujourd_hui}")
            
            if reservations_avant_aujourd_hui == 0:
                print("   🎉 CORRECTION RÉUSSIE: Aucun client parti avant aujourd'hui!")
            else:
                print("   ⚠️ PROBLÈME: Il y a encore des clients partis avant aujourd'hui")
        else:
            print("   ⚠️ Aucune réservation trouvée")
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return
    
    # Test 2: Vérifier les chambres actuelles
    print("\n2. Vérification des chambres actuelles...")
    try:
        chambres = get_chambres_actuelles_from_reservations(reservations)
        print(f"   ✅ {len(chambres)} chambres trouvées")
        
        if chambres:
            print("   🏨 Aperçu des chambres actuelles:")
            for i, chambre in enumerate(chambres[:5]):  # Afficher les 5 premières
                print(f"      {i+1}. Chambre {chambre.get('room_no')}")
                print(f"         Arrivée: {chambre.get('arrival')}")
                print(f"         Départ: {chambre.get('departure')}")
                print(f"         Clients: {len(chambre.get('clients', []))}")
                for client in chambre.get('clients', []):
                    print(f"           - {client.get('guest_name')} ({client.get('role')})")
        else:
            print("   ⚠️ Aucune chambre trouvée")
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return
    
    # Test 3: Vérifier les statuts
    print("\n3. Vérification des statuts...")
    statuts = {}
    for res in reservations:
        statut = res.get('statut', 'inconnu')
        statuts[statut] = statuts.get(statut, 0) + 1
    
    for statut, count in statuts.items():
        print(f"   📋 {statut}: {count} réservations")
    
    # Résumé
    print("\n" + "="*50)
    print("🎯 RÉSUMÉ DE LA CORRECTION")
    print("="*50)
    print(f"✅ Réservations totales: {len(reservations)}")
    print(f"✅ Chambres organisées: {len(chambres)}")
    
    if reservations_avant_aujourd_hui == 0:
        print("✅ CORRECTION RÉUSSIE")
        print("   • Aucun client parti avant aujourd'hui")
        print("   • Seuls les clients encore à l'hôtel sont affichés")
        print("   • La logique de date fonctionne correctement")
    else:
        print("❌ CORRECTION INCOMPLÈTE")
        print(f"   • {reservations_avant_aujourd_hui} clients partis avant aujourd'hui")
        print("   • Vérifier la logique de requête")
    
    print("\n🔧 Correction apportée:")
    print("   • Ajout de .gte('departure', today) à la requête en_cours")
    print("   • Seules les réservations avec départ >= aujourd'hui sont incluses")
    print("   • Les clients partis avant aujourd'hui sont exclus")

if __name__ == "__main__":
    test_correction_dates()
