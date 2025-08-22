#!/usr/bin/env python3
"""
Script pour debugger les clients actuels
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_reservations_actuelles, get_chambres_actuelles_from_reservations

def debug_clients_actuels():
    """Debugger les clients actuels"""
    print("🔍 === DEBUG CLIENTS ACTUELS ===\n")
    
    # Test 1: Récupérer les réservations actuelles
    print("1. Récupération des réservations actuelles...")
    try:
        reservations = get_reservations_actuelles()
        print(f"   ✅ {len(reservations)} réservations trouvées")
        
        if reservations:
            print("   📋 Aperçu des réservations:")
            for i, res in enumerate(reservations[:3]):  # Afficher les 3 premières
                print(f"      {i+1}. ID: {res.get('resv_name_id')}, Chambre: {res.get('room_no')}, Statut: {res.get('statut')}")
                print(f"         Arrivée: {res.get('arrival')}, Départ: {res.get('departure')}")
                print(f"         Client principal: {res.get('client_principal_id')}")
                print(f"         Client secondaire: {res.get('client_secondaire_id')}")
        else:
            print("   ⚠️ Aucune réservation trouvée")
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return
    
    # Test 2: Convertir en chambres actuelles
    print("\n2. Conversion en chambres actuelles...")
    try:
        chambres = get_chambres_actuelles_from_reservations(reservations)
        print(f"   ✅ {len(chambres)} chambres trouvées")
        
        if chambres:
            print("   🏨 Aperçu des chambres:")
            for i, chambre in enumerate(chambres[:3]):  # Afficher les 3 premières
                print(f"      {i+1}. Chambre: {chambre.get('room_no')}")
                print(f"         Catégorie: {chambre.get('room_category_label')}")
                print(f"         Clients: {len(chambre.get('clients', []))}")
                for client in chambre.get('clients', []):
                    print(f"           - {client.get('guest_name')} ({client.get('role')}) - VIP: {client.get('vip')}")
        else:
            print("   ⚠️ Aucune chambre trouvée")
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return
    
    # Test 3: Vérifier les données manquantes
    print("\n3. Vérification des données manquantes...")
    missing_room = 0
    missing_client = 0
    
    for res in reservations:
        if not res.get('room_no'):
            missing_room += 1
        if not res.get('client_principal_id') and not res.get('client_secondaire_id'):
            missing_client += 1
    
    print(f"   📊 Réservations sans chambre: {missing_room}")
    print(f"   📊 Réservations sans client: {missing_client}")
    
    # Test 4: Vérifier les statuts
    print("\n4. Vérification des statuts...")
    statuts = {}
    for res in reservations:
        statut = res.get('statut', 'inconnu')
        statuts[statut] = statuts.get(statut, 0) + 1
    
    for statut, count in statuts.items():
        print(f"   📋 {statut}: {count} réservations")
    
    # Résumé
    print("\n" + "="*50)
    print("🎯 RÉSUMÉ DU DEBUG")
    print("="*50)
    print(f"✅ Réservations totales: {len(reservations)}")
    print(f"✅ Chambres organisées: {len(chambres)}")
    print(f"✅ Données cohérentes: {'Oui' if len(chambres) > 0 else 'Non'}")
    
    if len(chambres) == 0:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        print("   • Aucune chambre trouvée")
        print("   • Vérifier les données de réservation")
        print("   • Vérifier les relations client-réservation")
    else:
        print("\n✅ TOUT SEMBLE CORRECT")
        print("   • Les données sont cohérentes")
        print("   • Les clients sont bien associés")
        print("   • Les chambres sont organisées")

if __name__ == "__main__":
    debug_clients_actuels()
