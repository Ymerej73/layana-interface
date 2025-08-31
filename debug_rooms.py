#!/usr/bin/env python3
"""
Script de debug pour vérifier les données des chambres
"""

import os
import sys
from datetime import datetime, date
from supabase import create_client, Client

# Configuration Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')  # Utiliser SUPABASE_KEY au lieu de SUPABASE_ANON_KEY

if not supabase_url or not supabase_key:
    print("❌ Variables d'environnement Supabase manquantes!")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def debug_rooms_data():
    """Debug des données des chambres"""
    
    print("🔍 DEBUG - Données des Chambres")
    print("=" * 60)
    
    # 1. Vérifier la date actuelle
    current_date = datetime.now().date()
    print(f"📅 Date actuelle: {current_date}")
    print(f"📅 Date actuelle (ISO): {current_date.isoformat()}")
    
    # 2. Récupérer TOUTES les réservations
    print("\n📋 Toutes les réservations:")
    try:
        all_reservations = supabase.table('reservations').select('*').execute()
        print(f"   Total réservations: {len(all_reservations.data)}")
        
        for i, res in enumerate(all_reservations.data[:5]):  # Afficher les 5 premières
            print(f"   {i+1}. {res.get('resv_name_id', 'N/A')} - Chambre {res.get('room_no', 'N/A')}")
            print(f"      Arrivée: {res.get('arrival', 'N/A')}")
            print(f"      Départ: {res.get('departure', 'N/A')}")
            print(f"      Client principal: {res.get('client_principal_id', 'N/A')}")
            print(f"      Client secondaire: {res.get('client_secondaire_id', 'N/A')}")
            print()
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 3. Tester notre logique de filtrage
    print("\n🔍 Test de notre logique de filtrage:")
    try:
        # Requête exacte comme dans notre API
        rooms_query = supabase.table('reservations').select(
            'resv_name_id, room_no, arrival, departure, client_principal_id, client_secondaire_id'
        ).gte('arrival', current_date.isoformat()).lte('departure', current_date.isoformat()).execute()
        
        print(f"   Réservations filtrées: {len(rooms_query.data)}")
        
        if rooms_query.data:
            for res in rooms_query.data:
                print(f"   ✅ Chambre {res.get('room_no')} - {res.get('resv_name_id')}")
                print(f"      Arrivée: {res.get('arrival')}")
                print(f"      Départ: {res.get('departure')}")
        else:
            print("   ❌ Aucune réservation trouvée avec notre filtrage")
            
            # Analyser pourquoi
            print("\n   🔍 Analyse du problème:")
            
            # Vérifier les réservations qui arrivent aujourd'hui
            arrivals_today = supabase.table('reservations').select('*').eq('arrival', current_date.isoformat()).execute()
            print(f"      Arrivées aujourd'hui: {len(arrivals_today.data)}")
            
            # Vérifier les réservations qui partent aujourd'hui
            departures_today = supabase.table('reservations').select('*').eq('departure', current_date.isoformat()).execute()
            print(f"      Départs aujourd'hui: {len(departures_today.data)}")
            
            # Vérifier les réservations en cours (arrivée <= aujourd'hui <= départ)
            ongoing = supabase.table('reservations').select('*').lte('arrival', current_date.isoformat()).gte('departure', current_date.isoformat()).execute()
            print(f"      En cours (arrivée <= aujourd'hui <= départ): {len(ongoing.data)}")
            
            if ongoing.data:
                print("      📋 Réservations en cours:")
                for res in ongoing.data:
                    print(f"         Chambre {res.get('room_no')} - {res.get('resv_name_id')}")
                    print(f"         Arrivée: {res.get('arrival')} - Départ: {res.get('departure')}")
            
    except Exception as e:
        print(f"   ❌ Erreur lors du filtrage: {e}")
    
    # 4. Vérifier le format des dates
    print("\n📅 Vérification du format des dates:")
    try:
        sample_reservations = supabase.table('reservations').select('arrival, departure').limit(3).execute()
        for i, res in enumerate(sample_reservations.data):
            print(f"   {i+1}. Arrivée: {res.get('arrival')} (type: {type(res.get('arrival'))})")
            print(f"      Départ: {res.get('departure')} (type: {type(res.get('departure'))})")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    debug_rooms_data()
