from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from supabase import create_client, Client
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import json
from functools import lru_cache, wraps
import time
import jwt
import pytz

# Charger les variables d'environnement
load_dotenv('config.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configuration Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')  # Clé anonyme pour l'authentification côté client

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être définis dans les variables d'environnement")

supabase: Client = create_client(supabase_url, supabase_key)

# Cache pour les données fréquemment utilisées
_cache = {}
_cache_timeout = 30  # 30 secondes pour améliorer les performances

# Fonction de décoration pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Fonction pour vérifier et valider le token JWT de Supabase
def verify_supabase_token(token):
    try:
        # Décoder le token sans vérification (pour obtenir les informations de base)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Erreur de vérification du token: {e}")
        return None

def get_cached_data(key, fetch_func, timeout=_cache_timeout):
    """Récupérer des données du cache ou les charger si nécessaire"""
    current_time = time.time()
    if key in _cache:
        data, timestamp = _cache[key]
        if current_time - timestamp < timeout:
            return data
    
    data = fetch_func()
    _cache[key] = (data, current_time)
    return data

def clear_cache():
    """Vider le cache"""
    _cache.clear()

# Contexte global pour toutes les pages
@app.context_processor
def inject_global_vars():
    """Injecter des variables globales dans tous les templates"""
    # Déterminer la langue (par défaut français)
    language = session.get('language', 'fr')
    
    if language == 'en':
        # Anglais
        days_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        months_en = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
        now = datetime.now()
        day_of_week = days_en[now.weekday()]
        month = months_en[now.month - 1]
        hour = now.hour
        # Récupérer le prénom de l'utilisateur connecté
        user_first_name = session.get('user_first_name', '')
        
        if 5 <= hour < 12:
            base_greeting = "Good morning"
        elif 12 <= hour < 18:
            base_greeting = "Good afternoon"
        else:
            base_greeting = "Good evening"
        
        # Ajouter le prénom si disponible
        if user_first_name:
            greeting = f"{base_greeting} {user_first_name}"
        else:
            greeting = base_greeting
            
        return {
            'current_date': f"{day_of_week} {now.day} {month} {now.year}",
            'current_date_short': now.strftime('%m/%d/%Y'),
            'message_accueil': greeting
        }
    else:
        # Français (par défaut)
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        mois_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                   'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        now = datetime.now()
        jour_semaine = jours_fr[now.weekday()]
        mois = mois_fr[now.month - 1]
        heure = now.hour
        # Récupérer le prénom de l'utilisateur connecté
        user_first_name = session.get('user_first_name', '')
        
        # Debug: afficher les informations de session
        print(f"DEBUG - Session info: {dict(session)}")
        print(f"DEBUG - User first name: '{user_first_name}'")
        
        if 5 <= heure < 12:
            base_greeting = "Bonjour"
        elif 12 <= heure < 18:
            base_greeting = "Bon après-midi"
        else:
            base_greeting = "Bonsoir"
        
        # Ajouter le prénom si disponible
        if user_first_name:
            message_accueil = f"{base_greeting} {user_first_name}"
        else:
            message_accueil = base_greeting
            
        return {
            'current_date': f"{jour_semaine} {now.day} {mois} {now.year}",
            'current_date_short': now.strftime('%d/%m/%Y'),
            'message_accueil': message_accueil
        }

# Filtres Jinja2 personnalisés
@app.template_filter('format_date')
def format_date(value):
    """Formater une date en format français"""
    if not value:
        return 'N/A'
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    return value.strftime('%d/%m/%Y')

@app.template_filter('duration_days')
def duration_days(start_date, end_date):
    """Calculer la durée en jours entre deux dates"""
    if not start_date or not end_date:
        return 0
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    return (end_date - start_date).days

@app.template_filter('nl2br')
def nl2br(value):
    """Convertir les retours à la ligne en <br>"""
    if not value:
        return ''
    return value.replace('\n', '<br>')

# Routes d'authentification
@app.route('/login')
def login():
    """Page de connexion"""
    # Si l'utilisateur est déjà connecté, rediriger vers le dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', 
                         supabase_url=supabase_url,
                         supabase_anon_key=supabase_anon_key)

@app.route('/register')
def register():
    """Page d'inscription"""
    # Si l'utilisateur est déjà connecté, rediriger vers le dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', 
                         supabase_url=supabase_url,
                         supabase_anon_key=supabase_anon_key)

@app.route('/auth/login', methods=['POST'])
def auth_login():
    """API pour traiter la connexion"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        if not access_token:
            return jsonify({'success': False, 'message': 'Token manquant'}), 400
        
        # Vérifier le token avec Supabase
        decoded_token = verify_supabase_token(access_token)
        if not decoded_token:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # Stocker les informations de session
        session['user_id'] = decoded_token.get('sub')
        session['user_email'] = decoded_token.get('email')
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        
        # Récupérer les informations supplémentaires de l'utilisateur
        user_metadata = decoded_token.get('user_metadata', {})
        
        # Debug: afficher les métadonnées
        print(f"DEBUG - Token decoded: {decoded_token}")
        print(f"DEBUG - User metadata: {user_metadata}")
        
        # Essayer de récupérer le prénom depuis différentes sources
        first_name = user_metadata.get('first_name', '')
        if not first_name:
            # Essayer depuis le nom complet
            full_name = user_metadata.get('full_name', '')
            if full_name:
                first_name = full_name.split(' ')[0]
        
        # Si toujours pas de prénom, essayer de l'extraire de l'email
        if not first_name:
            email = decoded_token.get('email', '')
            if email and '@' in email:
                # Extraire le prénom de l'email (ex: jeremy.caudan@layana.com -> jeremy)
                email_part = email.split('@')[0]
                if '.' in email_part:
                    first_name = email_part.split('.')[0].capitalize()
                else:
                    first_name = email_part.capitalize()
        
        session['user_name'] = user_metadata.get('full_name', '')
        session['user_role'] = user_metadata.get('role', 'Utilisateur')
        session['user_first_name'] = first_name
        session['user_last_name'] = user_metadata.get('last_name', '')
        
        # Debug: afficher les informations de session après stockage
        print(f"DEBUG - Session after login: {dict(session)}")
        print(f"DEBUG - First name extracted: '{first_name}'")
        print(f"DEBUG - Email used for fallback: '{decoded_token.get('email', '')}'")
        
        return jsonify({'success': True, 'message': 'Connexion réussie'})
        
    except Exception as e:
        print(f"Erreur lors de la connexion: {e}")
        return jsonify({'success': False, 'message': 'Erreur lors de la connexion'}), 500

@app.route('/auth/logout')
def auth_logout():
    """Déconnexion"""
    # Vider la session Flask
    session.clear()
    
    # Rediriger vers la page de connexion avec un paramètre pour forcer la déconnexion Supabase
    return redirect(url_for('login', logout='true'))

@app.route('/debug/session')
@login_required
def debug_session():
    """Route de debug pour vérifier la session"""
    return jsonify({
        'session_data': dict(session),
        'user_first_name': session.get('user_first_name', 'Non défini'),
        'user_name': session.get('user_name', 'Non défini'),
        'user_role': session.get('user_role', 'Non défini')
    })

@app.route('/')
@login_required
def dashboard():
    """Page d'accueil avec vue d'ensemble"""
    try:
        # Récupérer toutes les données en parallèle avec cache
        def fetch_stats():
            return get_dashboard_stats()
        
        def fetch_reservations():
            return get_reservations_jour_with_clients()
        
        # Utiliser le cache pour les données
        stats = get_cached_data('dashboard_stats', fetch_stats, 60)  # Cache plus long pour les stats
        reservations_jour = get_cached_data('reservations_jour', fetch_reservations, 30)
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             reservations_jour=reservations_jour)
    except Exception as e:
        flash(f"Erreur lors du chargement du tableau de bord: {str(e)}", 'error')
        return render_template('dashboard.html', stats={}, reservations_jour=[])

@app.route('/clients')
@login_required
def clients():
    """Page de gestion des clients"""
    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = 20
        
        # Cache key basé sur la recherche et la page
        cache_key = f'clients_{search}_{page}'
        
        def fetch_clients():
            return get_clients(search, page, per_page)
        
        clients_data = get_cached_data(cache_key, fetch_clients, 30)
        
        return render_template('clients.html', 
                             clients=clients_data['clients'],
                             total_pages=clients_data['total_pages'],
                             current_page=page,
                             search=search)
    except Exception as e:
        flash(f"Erreur lors du chargement des clients: {str(e)}", 'error')
        return render_template('clients.html', clients=[], total_pages=0, current_page=1, search='')

@app.route('/clients-actuels')
@login_required
def clients_actuels():
    """Page des chambres actuellement occupées"""
    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = 12  # 12 chambres par page pour un affichage en grille
        
        # Cache key basé sur la recherche et la page
        cache_key = f'clients_actuels_{search}_{page}'
        
        def fetch_chambres_data():
            # Récupérer les réservations actuelles (cachées séparément)
            reservations = get_cached_data('reservations_actuelles', get_reservations_actuelles, 30)
            
            # Convertir en chambres actuelles
            chambres_actuelles = get_chambres_actuelles_from_reservations(reservations)
            
            # Filtrage par recherche
            if search:
                chambres_actuelles = [
                    chambre for chambre in chambres_actuelles
                    if search.lower() in chambre['room_no'].lower() or
                    any(search.lower() in client['guest_name'].lower() for client in chambre['clients'])
                ]
            
            # Pagination
            total = len(chambres_actuelles)
            start = (page - 1) * per_page
            end = start + per_page
            chambres_paginees = chambres_actuelles[start:end]
            total_pages = (total + per_page - 1) // per_page
            
            # Calculer le total VIP (optimisé)
            total_vip = sum(
                len([client for client in chambre['clients'] if client.get('vip') and client.get('vip') != ''])
                for chambre in chambres_actuelles
            )
            
            return {
                'chambres_paginees': chambres_paginees,
                'total_vip': total_vip,
                'total_pages': total_pages,
                'total_chambres': total
            }
        
        # Utiliser le cache avec la clé spécifique
        chambres_data = get_cached_data(cache_key, fetch_chambres_data, 30)
        
        return render_template('clients_actuels.html', 
                             chambres_actuelles=chambres_data['chambres_paginees'],
                             total_vip=chambres_data['total_vip'],
                             total_pages=chambres_data['total_pages'],
                             current_page=page,
                             search=search,
                             total_chambres=chambres_data['total_chambres'])
    except Exception as e:
        flash(f"Erreur lors du chargement des clients actuels: {str(e)}", 'error')
        return render_template('clients_actuels.html', 
                             chambres_actuelles=[], 
                             total_vip=0,
                             total_pages=0,
                             current_page=1,
                             search='',
                             total_chambres=0)

@app.route('/reservations')
@login_required
def reservations():
    """Page de gestion des réservations"""
    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = 20
        
        # Cache key basé sur la recherche et la page
        cache_key = f'reservations_{search}_{page}'
        
        def fetch_reservations():
            return get_reservations(search, page, per_page)
        
        reservations_data = get_cached_data(cache_key, fetch_reservations, 30)
        
        today_date = datetime.now().strftime('%d %b %Y')
        
        return render_template('reservations.html', 
                             reservations=reservations_data['reservations'],
                             total_pages=reservations_data['total_pages'],
                             current_page=page,
                             search=search,
                             today_date=today_date)
    except Exception as e:
        flash(f"Erreur lors du chargement des réservations: {str(e)}", 'error')
        today_date = datetime.now().strftime('%d %b %Y')
        return render_template('reservations.html', reservations=[], total_pages=0, current_page=1, search='', today_date=today_date)

@app.route('/client/<int:client_id>')
@login_required
def client_detail(client_id):
    """Page de détail d'un client"""
    try:
        def fetch_client():
            return get_client_by_id(client_id)
        
        def fetch_reservations():
            return get_reservations_par_client(client_id)
        
        client = get_cached_data(f'client_{client_id}', fetch_client, 60)
        reservations = get_cached_data(f'client_reservations_{client_id}', fetch_reservations, 30)
        
        if not client:
            flash('Client non trouvé', 'error')
            return redirect(url_for('clients'))
        
        return render_template('client_detail.html', 
                             client=client,
                             reservations=reservations)
    except Exception as e:
        flash(f"Erreur lors du chargement du client: {str(e)}", 'error')
        return redirect(url_for('clients'))

@app.route('/reservation/<resv_name_id>')
@login_required
def reservation_detail(resv_name_id):
    """Page de détail d'une réservation"""
    try:
        def fetch_reservation():
            return get_reservation_by_id(resv_name_id)
        
        def fetch_client_principal():
            reservation = get_reservation_by_id(resv_name_id)
            if reservation and reservation.get('client_principal_id'):
                return get_client_by_id(reservation['client_principal_id'])
            return None
        
        def fetch_client_secondaire():
            reservation = get_reservation_by_id(resv_name_id)
            if reservation and reservation.get('client_secondaire_id'):
                return get_client_by_id(reservation['client_secondaire_id'])
            return None
        
        reservation = get_cached_data(f'reservation_{resv_name_id}', fetch_reservation, 30)
        client_principal = get_cached_data(f'client_principal_{resv_name_id}', fetch_client_principal, 30)
        client_secondaire = get_cached_data(f'client_secondaire_{resv_name_id}', fetch_client_secondaire, 30)
        
        if not reservation:
            flash('Réservation non trouvée', 'error')
            return redirect(url_for('reservations'))
        
        return render_template('reservation_detail.html', 
                             reservation=reservation,
                             client_principal=client_principal,
                             client_secondaire=client_secondaire)
    except Exception as e:
        flash(f"Erreur lors du chargement de la réservation: {str(e)}", 'error')
        return redirect(url_for('reservations'))

# API Routes pour les modifications
@app.route('/api/client/<int:client_id>', methods=['GET', 'PUT'])
@login_required
def api_client(client_id):
    """API pour récupérer ou mettre à jour un client"""
    if request.method == 'GET':
        try:
            def fetch_client():
                return get_client_by_id(client_id)
            
            client = get_cached_data(f'client_{client_id}', fetch_client, 30)
            if client:
                return jsonify({'success': True, 'client': client})
            else:
                return jsonify({'success': False, 'message': 'Client non trouvé'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Mise à jour du client
            result = supabase.table('clients').update(data).eq('id', client_id).execute()
            
            if result.data:
                # Invalider le cache pour ce client
                cache_keys_to_clear = [f'client_{client_id}', 'clients_*', 'dashboard_stats', 'clients_recents']
                for key in list(_cache.keys()):
                    if any(pattern.replace('*', '') in key for pattern in cache_keys_to_clear):
                        del _cache[key]
                
                return jsonify({'success': True, 'message': 'Client mis à jour avec succès', 'data': result.data})
            else:
                return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour'}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reservation/<resv_name_id>', methods=['GET', 'PUT'])
@login_required
def api_reservation(resv_name_id):
    """API pour récupérer ou mettre à jour une réservation"""
    if request.method == 'GET':
        try:
            def fetch_reservation():
                return get_reservation_by_id(resv_name_id)
            
            reservation = get_cached_data(f'reservation_{resv_name_id}', fetch_reservation, 30)
            if reservation:
                return jsonify({'success': True, 'reservation': reservation})
            else:
                return jsonify({'success': False, 'message': 'Réservation non trouvée'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Mise à jour de la réservation
            result = supabase.table('reservations').update(data).eq('resv_name_id', resv_name_id).execute()
            
            if result.data:
                # Invalider le cache pour cette réservation
                cache_keys_to_clear = [f'reservation_{resv_name_id}', 'reservations_*', 'dashboard_stats', 'reservations_jour', 'chambres_actuelles']
                for key in list(_cache.keys()):
                    if any(pattern.replace('*', '') in key for pattern in cache_keys_to_clear):
                        del _cache[key]
                
                return jsonify({'success': True, 'message': 'Réservation mise à jour avec succès'})
            else:
                return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour'}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

# Route pour vider le cache (utile pour le développement)
@app.route('/clear-cache')
def clear_cache_route():
    """Vider le cache (route de développement)"""
    clear_cache()
    return jsonify({'success': True, 'message': 'Cache vidé'})

@app.route('/api/calendar/<int:year>/<int:month>')
@login_required
def get_calendar_api(year, month):
    """API pour récupérer les données du calendrier"""
    try:
        calendar_data = get_calendar_data(year, month)
        return jsonify(calendar_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status')
@login_required
def get_system_status():
    """API pour vérifier le statut du système"""
    try:
        start_time = time.time()
        
        # Vérifier la connexion Supabase
        try:
            # Test simple de connexion
            test_result = supabase.table('clients').select('id').limit(1).execute()
            supabase_status = 'online'
            supabase_response_time = round((time.time() - start_time) * 1000, 2)
        except Exception as e:
            supabase_status = 'offline'
            supabase_response_time = None
        
        # Vérifier la base de données
        try:
            db_start = time.time()
            db_test = supabase.table('reservations').select('resv_name_id').limit(1).execute()
            database_status = 'online'
            db_response_time = round((time.time() - db_start) * 1000, 2)
        except Exception as e:
            database_status = 'offline'
            db_response_time = None
        
        # Vérifier l'API
        api_status = 'online'
        api_response_time = round((time.time() - start_time) * 1000, 2)
        
        status_data = {
            'supabase': {
                'status': supabase_status,
                'response_time': supabase_response_time
            },
            'database': {
                'status': database_status,
                'response_time': db_response_time
            },
            'api': {
                'status': api_status,
                'response_time': api_response_time
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
@login_required
def settings():
    """Page des paramètres utilisateur"""
    return render_template('settings.html')

@app.route('/api/settings/language', methods=['POST'])
@login_required
def set_language():
    """API pour changer la langue"""
    try:
        data = request.get_json()
        language = data.get('language', 'fr')
        
        # Sauvegarder la langue dans la session
        session['language'] = language
        
        return jsonify({'success': True, 'language': language})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings/save', methods=['POST'])
@login_required
def save_settings():
    """API pour sauvegarder les paramètres"""
    try:
        data = request.get_json()
        
        # Sauvegarder les paramètres dans la session
        session['user_settings'] = data
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Fonctions utilitaires optimisées
def get_dashboard_stats():
    """Récupérer les statistiques du tableau de bord"""
    try:
        # Requête unique pour toutes les statistiques
        today = date.today().isoformat()
        
        # Requêtes optimisées avec des sélections spécifiques
        clients_count = supabase.table('clients').select('id', count='exact').execute()
        all_reservations = supabase.table('reservations').select('*').execute()
        
        # Calculer les statistiques à partir des données
        total_clients = clients_count.count if hasattr(clients_count, 'count') else len(clients_count.data)
        
        reservations_data = all_reservations.data
        
        # Réservations du jour (arrivées aujourd'hui)
        reservations_jour_count = len([r for r in reservations_data if r.get('arrival') == today])
        
        # Réservations en cours (utiliser la même logique que get_reservations_actuelles)
        reservations_actuelles = get_reservations_actuelles()
        reservations_en_cours = len(reservations_actuelles)
        
        # Réservations futures (statut futures ET arrivée > aujourd'hui)
        reservations_futures = len([r for r in reservations_data 
                                  if r.get('statut') == 'futures' and r.get('arrival') > today])
        
        # Réservations terminées (statut terminee OU départ < aujourd'hui)
        reservations_terminees = len([r for r in reservations_data 
                                    if r.get('statut') == 'terminee' or 
                                    (r.get('departure') and r.get('departure') < today)])
        
        stats = {
            'total_clients': total_clients,
            'reservations_jour': reservations_jour_count,
            'reservations_en_cours': reservations_en_cours,
            'reservations_futures': reservations_futures,
            'reservations_terminees': reservations_terminees
        }
        
        return stats
    except Exception as e:
        print(f"Erreur get_dashboard_stats: {str(e)}")
        return {}

def get_reservations_jour():
    """Récupérer les réservations du jour"""
    try:
        today = date.today().isoformat()
        result = supabase.table('reservations').select('*').eq('arrival', today).execute()
        return result.data
    except Exception as e:
        pass
        return []

def get_reservations_jour_with_clients():
    """Récupérer les réservations du jour avec les informations des clients"""
    try:
        reservations = get_reservations_jour()
        
        # Récupérer tous les IDs de clients en une seule fois
        client_ids = set()
        for reservation in reservations:
            if reservation.get('client_principal_id'):
                client_ids.add(reservation['client_principal_id'])
            if reservation.get('client_secondaire_id'):
                client_ids.add(reservation['client_secondaire_id'])
        
        # Récupérer tous les clients en une seule requête
        clients_data = {}
        if client_ids:
            clients_result = supabase.table('clients').select('*').in_('id', list(client_ids)).execute()
            for client in clients_result.data:
                clients_data[client['id']] = client
        
        # Enrichir les réservations avec les données des clients
        for reservation in reservations:
            reservation['client_principal'] = clients_data.get(reservation.get('client_principal_id'))
            reservation['client_secondaire'] = clients_data.get(reservation.get('client_secondaire_id'))
        
        return reservations
    except Exception as e:
        pass
        return []

def get_clients_recents():
    """Récupérer les clients récents"""
    try:
        result = supabase.table('clients').select('*').order('id', desc=True).limit(5).execute()
        return result.data
    except Exception as e:
        pass
        return []

def get_clients(search='', page=1, per_page=20):
    """Récupérer les clients avec pagination et recherche"""
    try:
        query = supabase.table('clients').select('*')
        
        if search:
            # Recherche dans guest_name, guest_title et guest_name_id
            query = query.or_(f'guest_name.ilike.%{search}%,guest_title.ilike.%{search}%,guest_name_id.ilike.%{search}%')
        
        # Calculer l'offset
        offset = (page - 1) * per_page
        
        # Récupérer les données avec pagination
        result = query.range(offset, offset + per_page - 1).execute()
        
        # Récupérer le total pour la pagination
        total_query = supabase.table('clients').select('id', count='exact')
        if search:
            total_query = total_query.or_(f'guest_name.ilike.%{search}%,guest_title.ilike.%{search}%,guest_name_id.ilike.%{search}%')
        total_result = total_query.execute()
        
        total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            'clients': result.data,
            'total_pages': total_pages
        }
    except Exception as e:
        print(f"Erreur get_clients: {str(e)}")
        return {'clients': [], 'total_pages': 0}

def get_reservations(search='', page=1, per_page=20):
    """Récupérer les réservations avec pagination et recherche"""
    try:
        if search:
            # Si on cherche par nom de client, d'abord trouver les clients correspondants
            clients_search = supabase.table('clients').select('id').or_(f'guest_name.ilike.%{search}%,guest_title.ilike.%{search}%,guest_name_id.ilike.%{search}%').execute()
            matching_client_ids = [client['id'] for client in clients_search.data]
            
            # Construire la requête pour les réservations
            query = supabase.table('reservations').select('*')
            
            # Recherche par ID réservation, chambre OU clients correspondants
            if matching_client_ids:
                # Créer les conditions pour les clients
                client_conditions = []
                for client_id in matching_client_ids:
                    client_conditions.append(f'client_principal_id.eq.{client_id},client_secondaire_id.eq.{client_id}')
                
                # Combiner avec la recherche directe
                search_conditions = f'resv_name_id.ilike.%{search}%,room_no.ilike.%{search}%'
                if client_conditions:
                    search_conditions += ',' + ','.join(client_conditions)
                
                query = query.or_(search_conditions)
            else:
                # Si aucun client ne correspond, chercher seulement par ID réservation et chambre
                query = query.or_(f'resv_name_id.ilike.%{search}%,room_no.ilike.%{search}%')
        else:
            query = supabase.table('reservations').select('*')
        
        # Calculer l'offset
        offset = (page - 1) * per_page
        
        # Récupérer les données avec pagination
        result = query.range(offset, offset + per_page - 1).execute()
        
        # Récupérer le total pour la pagination (approximatif pour la recherche par client)
        if search:
            # Pour la pagination, on utilise une approche simplifiée
            total_query = supabase.table('reservations').select('resv_name_id', count='exact')
            if matching_client_ids:
                client_conditions = []
                for client_id in matching_client_ids:
                    client_conditions.append(f'client_principal_id.eq.{client_id},client_secondaire_id.eq.{client_id}')
                search_conditions = f'resv_name_id.ilike.%{search}%,room_no.ilike.%{search}%'
                if client_conditions:
                    search_conditions += ',' + ','.join(client_conditions)
                total_query = total_query.or_(search_conditions)
            else:
                total_query = total_query.or_(f'resv_name_id.ilike.%{search}%,room_no.ilike.%{search}%')
        else:
            total_query = supabase.table('reservations').select('resv_name_id', count='exact')
        total_result = total_query.execute()
        
        total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        total_pages = (total_count + per_page - 1) // per_page
        
        # Enrichir les réservations avec les données des clients
        reservations = result.data
        client_ids = set()
        for reservation in reservations:
            if reservation.get('client_principal_id'):
                client_ids.add(reservation['client_principal_id'])
            if reservation.get('client_secondaire_id'):
                client_ids.add(reservation['client_secondaire_id'])
        
        # Récupérer tous les clients en une seule requête
        clients_data = {}
        if client_ids:
            clients_result = supabase.table('clients').select('*').in_('id', list(client_ids)).execute()
            for client in clients_result.data:
                clients_data[client['id']] = client
        
        # Enrichir les réservations
        for reservation in reservations:
            reservation['client_principal'] = clients_data.get(reservation.get('client_principal_id'))
            reservation['client_secondaire'] = clients_data.get(reservation.get('client_secondaire_id'))
        
        return {
            'reservations': reservations,
            'total_pages': total_pages
        }
    except Exception as e:
        print(f"Erreur get_reservations: {str(e)}")
        return {'reservations': [], 'total_pages': 0}

def get_client_by_id(client_id):
    """Récupérer un client par son ID"""
    try:
        result = supabase.table('clients').select('*').eq('id', client_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        pass
        return None

def get_reservation_by_id(resv_name_id):
    """Récupérer une réservation par son ID"""
    try:
        result = supabase.table('reservations').select('*').eq('resv_name_id', resv_name_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        pass
        return None

def get_reservations_par_client(client_id):
    """Récupérer toutes les réservations d'un client"""
    try:
        result = supabase.table('reservations').select('*').or_(f'client_principal_id.eq.{client_id},client_secondaire_id.eq.{client_id}').execute()
        return result.data
    except Exception as e:
        pass
        return []

def get_reservations_actuelles():
    """Récupérer les réservations actuellement en cours"""
    try:
        today = date.today().isoformat()
        
        # Récupérer les réservations avec statut "en_cours" ET qui sont encore à l'hôtel aujourd'hui
        result_en_cours = supabase.table('reservations').select('*').eq('statut', 'en_cours').gte('departure', today).execute()
        
        # Récupérer aussi les réservations actuelles par date (pour les nouveaux arrivants)
        result_par_date = supabase.table('reservations').select('*').lte('arrival', today).gte('departure', today).execute()
        
        # Combiner les deux résultats en évitant les doublons
        reservations_actuelles = {}
        
        # Ajouter les réservations en cours qui sont encore à l'hôtel
        for res in result_en_cours.data:
            reservations_actuelles[res['resv_name_id']] = res
        
        # Ajouter les réservations par date (peuvent remplacer les en_cours si plus récentes)
        for res in result_par_date.data:
            reservations_actuelles[res['resv_name_id']] = res
        
        return list(reservations_actuelles.values())
    except Exception as e:
        print(f"Erreur get_reservations_actuelles: {str(e)}")
        return []

def get_calendar_data(year=None, month=None):
    """Récupérer les données du calendrier pour un mois donné"""
    try:
        if not year or not month:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Calculer le premier et dernier jour du mois
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Récupérer TOUTES les réservations en une seule requête
        result = supabase.table('reservations').select('*').execute()
        
        # Collecter tous les IDs de clients uniques
        client_ids = set()
        for reservation in result.data:
            if reservation.get('client_principal_id'):
                client_ids.add(reservation['client_principal_id'])
            if reservation.get('client_secondaire_id'):
                client_ids.add(reservation['client_secondaire_id'])
        
        # Récupérer TOUS les clients en une seule requête
        clients_data = {}
        if client_ids:
            client_ids_list = list(client_ids)
            # Diviser en chunks de 100 pour éviter les limites de requête
            chunk_size = 100
            for i in range(0, len(client_ids_list), chunk_size):
                chunk = client_ids_list[i:i + chunk_size]
                client_result = supabase.table('clients').select('*').in_('id', chunk).execute()
                for client in client_result.data:
                    clients_data[client['id']] = client
        
        # Organiser les données par jour
        calendar_data = {}
        
        for reservation in result.data:
            try:
                # Récupérer les données du client depuis le cache
                client_principal = clients_data.get(reservation.get('client_principal_id'))
                
                # Calculer les jours de présence
                arrival_str = reservation.get('arrival')
                departure_str = reservation.get('departure')
                
                if not arrival_str or not departure_str:
                    continue
                
                # Gérer les différents formats de date
                try:
                    if 'T' in arrival_str:
                        arrival = datetime.fromisoformat(arrival_str.replace('Z', '+00:00')).date()
                    else:
                        arrival = datetime.strptime(arrival_str, '%Y-%m-%d').date()
                    
                    if 'T' in departure_str:
                        departure = datetime.fromisoformat(departure_str.replace('Z', '+00:00')).date()
                    else:
                        departure = datetime.strptime(departure_str, '%Y-%m-%d').date()
                except Exception as e:
                    continue
                
                # Vérifier si la réservation chevauche le mois demandé
                if departure < start_date or arrival > end_date:
                    continue
                
                # Limiter aux jours du mois demandé
                start_day = max(arrival, start_date)
                end_day = min(departure, end_date)
                
                current_day = start_day
                while current_day <= end_day:
                    day_key = current_day.isoformat()
                    if day_key not in calendar_data:
                        calendar_data[day_key] = {
                            'arrivals': [],
                            'departures': [],
                            'guests': []
                        }
                    
                    # Ajouter aux clients présents
                    calendar_data[day_key]['guests'].append({
                        'reservation_id': reservation['resv_name_id'],
                        'client_name': client_principal['guest_name'] if client_principal else 'Client inconnu',
                        'client_id': client_principal['id'] if client_principal else None,
                        'room_no': reservation.get('room_no', 'Non assignée'),
                        'arrival': reservation['arrival'],
                        'departure': reservation['departure']
                    })
                    
                    # Ajouter aux arrivées si c'est le jour d'arrivée
                    if current_day == arrival:
                        calendar_data[day_key]['arrivals'].append({
                            'reservation_id': reservation['resv_name_id'],
                            'client_name': client_principal['guest_name'] if client_principal else 'Client inconnu',
                            'client_id': client_principal['id'] if client_principal else None,
                            'room_no': reservation.get('room_no', 'Non assignée')
                        })
                    
                    # Ajouter aux départs si c'est le jour de départ
                    if current_day == departure:
                        calendar_data[day_key]['departures'].append({
                            'reservation_id': reservation['resv_name_id'],
                            'client_name': client_principal['guest_name'] if client_principal else 'Client inconnu',
                            'client_id': client_principal['id'] if client_principal else None,
                            'room_no': reservation.get('room_no', 'Non assignée')
                        })
                    
                    current_day += timedelta(days=1)
                    
            except Exception as e:
                continue
        

        
        return {
            'year': year,
            'month': month,
            'calendar_data': calendar_data
        }
        
    except Exception as e:
        print(f"Erreur get_calendar_data: {str(e)}")
        return {'year': year, 'month': month, 'calendar_data': {}}

def get_chambres_actuelles_from_reservations(reservations):
    """Organiser les réservations actuelles par chambre"""
    chambres_actuelles = {}
    
    # Collecter tous les IDs de clients pour un batch fetch
    client_ids = set()
    for reservation in reservations:
        if reservation.get('client_principal_id'):
            client_ids.add(reservation['client_principal_id'])
        if reservation.get('client_secondaire_id'):
            client_ids.add(reservation['client_secondaire_id'])
    
    # Récupérer tous les clients en une seule requête
    clients_data = {}
    if client_ids:
        client_ids_list = list(client_ids)
        # Diviser en chunks de 100 pour éviter les limites de requête
        chunk_size = 100
        for i in range(0, len(client_ids_list), chunk_size):
            chunk = client_ids_list[i:i + chunk_size]
            try:
                client_result = supabase.table('clients').select('*').in_('id', chunk).execute()
                for client in client_result.data:
                    clients_data[client['id']] = client
            except Exception as e:
                print(f"Erreur batch fetch clients: {str(e)}")
                continue
    
    # Organiser les réservations par chambre
    for reservation in reservations:
        room_no = reservation.get('room_no')
        if not room_no:
            continue
            
        if room_no not in chambres_actuelles:
            chambres_actuelles[room_no] = {
                'room_no': room_no,
                'room_category_label': reservation.get('room_category_label', 'Chambre Standard'),
                'resv_name_id': reservation['resv_name_id'],
                'arrival': reservation.get('arrival'),
                'departure': reservation.get('departure'),
                'clients': []
            }
        
        client_principal = None
        vip_status = None
        
        if reservation.get('client_principal_id'):
            client_principal = clients_data.get(reservation['client_principal_id'])
            if client_principal:
                vip_status = client_principal.get('vip')
                chambres_actuelles[room_no]['clients'].append({
                    'id': client_principal['id'],
                    'guest_name': client_principal['guest_name'],
                    'guest_title': client_principal.get('guest_title', ''),
                    'vip': vip_status,
                    'role': 'Principal'
                })
        
        if reservation.get('client_secondaire_id'):
            client_secondaire = clients_data.get(reservation['client_secondaire_id'])
            if client_secondaire:
                secondaire_vip = vip_status if vip_status else client_secondaire.get('vip')
                chambres_actuelles[room_no]['clients'].append({
                    'id': client_secondaire['id'],
                    'guest_name': client_secondaire['guest_name'],
                    'guest_title': client_secondaire.get('guest_title', ''),
                    'vip': secondaire_vip,
                    'role': 'Secondaire'
                })
    
    return list(chambres_actuelles.values())

@app.route('/test-vip')
def test_vip():
    """Route de test pour ajouter des données VIP"""
    try:
        # Récupérer les réservations actuelles
        reservations = get_reservations_actuelles()
        
        # Collecter tous les IDs de clients
        client_ids = set()
        for reservation in reservations:
            if reservation.get('client_principal_id'):
                client_ids.add(reservation['client_principal_id'])
            if reservation.get('client_secondaire_id'):
                client_ids.add(reservation['client_secondaire_id'])
        
        # Mettre à jour les premiers clients avec des statuts VIP
        updates = []
        client_ids_list = list(client_ids)[:10]  # Limiter à 10 clients
        
        for i, client_id in enumerate(client_ids_list):
            vip_status = f'VIP{i % 3 + 1}' if i % 3 != 0 else 'VIP1'
            updates.append({'id': client_id, 'vip': vip_status})
        
        # Mettre à jour en base
        for update in updates:
            result = supabase.table('clients').update({'vip': update['vip']}).eq('id', update['id']).execute()
        
        # Vider le cache après mise à jour
        clear_cache()
        
        return jsonify({'success': True, 'message': f'Données VIP ajoutées pour {len(updates)} clients', 'client_ids': client_ids_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
