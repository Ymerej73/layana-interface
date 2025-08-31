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
import openai

# Fonction utilitaire pour parser les dates
def parse_date(date_string):
    """Parser une date depuis un string ISO ou autre format"""
    if not date_string:
        return None
    
    try:
        # Essayer le format ISO d'abord
        if isinstance(date_string, str):
            return date.fromisoformat(date_string)
        elif isinstance(date_string, date):
            return date_string
        elif isinstance(date_string, datetime):
            return date_string.date()
        else:
            return None
    except (ValueError, TypeError):
        try:
            # Essayer d'autres formats courants
            return datetime.strptime(str(date_string), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            print(f"Impossible de parser la date: {date_string}")
            return None

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

# Configuration OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# Initialiser le client OpenAI global
openai_client = None
if openai_api_key:
    try:
        openai_client = openai.OpenAI(api_key=openai_api_key)
        print("✅ Client OpenAI initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur initialisation OpenAI: {e}")
        openai_client = None

if openai_api_key:
    openai.api_key = openai_api_key
    print("OpenAI configuré avec succès")
else:
    print("Attention: OPENAI_API_KEY non configurée")

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

# Système de localisation
def load_translations(language):
    """Charger les traductions pour une langue donnée"""
    try:
        with open(f'locales/{language}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fichier de traduction non trouvé pour la langue: {language}")
        return {}

def get_text(key, language=None):
    """Obtenir le texte traduit pour une clé donnée"""
    if language is None:
        language = session.get('language', 'fr')
    
    translations = load_translations(language)
    
    # Naviguer dans la structure JSON (ex: "dashboard.welcome")
    keys = key.split('.')
    value = translations
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Retourner la clé si la traduction n'est pas trouvée
            return key
    
    return value if isinstance(value, str) else key

# Contexte global pour toutes les pages
@app.context_processor
def inject_global_vars():
    """Injecter des variables globales dans tous les templates"""
    # Déterminer la langue (par défaut français)
    language = session.get('language', 'fr')
    
    # Charger les traductions
    translations = load_translations(language)
    
    # Déterminer le message de salutation selon l'heure
    now = datetime.now()
    hour = now.hour
    
    if language == 'en':
        # Anglais
        days_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        months_en = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
        day_of_week = days_en[now.weekday()]
        month = months_en[now.month - 1]
        
        if 5 <= hour < 12:
            base_greeting = get_text('dashboard.greeting_morning', 'en')
        elif 12 <= hour < 18:
            base_greeting = get_text('dashboard.greeting_afternoon', 'en')
        else:
            base_greeting = get_text('dashboard.greeting_evening', 'en')
    else:
        # Français
        days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                     'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        day_of_week = days_fr[now.weekday()]
        month = months_fr[now.month - 1]
        
        if 5 <= hour < 12:
            base_greeting = get_text('dashboard.greeting_morning', 'fr')
        elif 12 <= hour < 18:
            base_greeting = get_text('dashboard.greeting_afternoon', 'fr')
        else:
            base_greeting = get_text('dashboard.greeting_evening', 'fr')
    
    # Récupérer le prénom de l'utilisateur connecté
    user_first_name = session.get('user_first_name', '')
    
    # Ajouter le prénom si disponible
    if user_first_name:
        greeting = f"{base_greeting} {user_first_name}"
    else:
        greeting = base_greeting
        
    return {
        'current_date': f"{day_of_week} {now.day} {month} {now.year}",
        'current_date_short': now.strftime('%m/%d/%Y') if language == 'en' else now.strftime('%d/%m/%Y'),
        'message_accueil': greeting,
        'user_first_name': user_first_name,
        'user_email': session.get('user_email', ''),
        'user_name': session.get('user_name', ''),
        'user_role': session.get('user_role', ''),
        'language': language,
        'translations': translations,
        'get_text': get_text
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

# Route pour changer la langue
@app.route('/change-language/<language>')
def change_language(language):
    """Changer la langue de l'interface"""
    if language in ['fr', 'en']:
        session['language'] = language
        # Rediriger vers la page précédente ou le dashboard
        return redirect(request.referrer or url_for('dashboard'))
    return redirect(url_for('dashboard'))

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

@app.route('/api/departures/today')
@login_required
def get_today_departures():
    """API pour récupérer les départs du jour"""
    try:
        departures = get_departures_jour_with_clients()
        return jsonify(departures)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/status')
def get_rooms_status():
    """API pour récupérer l'état des chambres occupées"""
    try:
        print("DEBUG - Début de get_rooms_status")
        
        # Récupérer toutes les réservations avec un numéro de chambre
        response = supabase.table('reservations').select(
            'resv_name_id, room_no, statut, client_principal_id, client_secondaire_id'
        ).not_.is_('room_no', 'null').execute()
        
        if response.data:
            print(f"DEBUG - Réservations trouvées: {len(response.data)}")
            
            # Filtrer les réservations en cours
            occupied_rooms = []
            
            for reservation in response.data:
                # Vérifier si la chambre est occupée (statut = 'en_cours')
                if reservation.get('statut') == 'en_cours':
                    print(f"DEBUG - Chambre {reservation['room_no']} en cours d'occupation")
                    
                    # Vérifier si la chambre a des clients
                    has_clients = False
                    vip_level = "Standard"
                    client_name = "Client"
                    
                    # Vérifier le client principal
                    if reservation.get('client_principal_id'):
                        try:
                            client_response = supabase.table('clients').select('guest_name, vip').eq('id', reservation['client_principal_id']).execute()
                            if client_response.data:
                                has_clients = True
                                client_info = client_response.data[0]
                                # Récupérer le nom du client
                                if client_info.get('guest_name'):
                                    client_name = client_info['guest_name']
                                # Récupérer le niveau VIP
                                client_vip = client_info.get('vip', '')
                                if client_vip and client_vip.strip():
                                    vip_level = client_vip
                                    print(f"DEBUG - Chambre {reservation['room_no']}: VIP {vip_level}, Client: {client_name}")
                        except Exception as e:
                            print(f"DEBUG - Erreur client principal: {e}")
                    
                    # Vérifier le client secondaire
                    if reservation.get('client_secondaire_id'):
                        try:
                            client_response = supabase.table('clients').select('vip').eq('id', reservation['client_secondaire_id']).execute()
                            if client_response.data:
                                has_clients = True
                                # Prendre le niveau VIP le plus élevé
                                client_vip = client_response.data[0].get('vip', '')
                                if client_vip and client_vip.strip():
                                    # Si le client secondaire a un niveau VIP plus élevé, l'utiliser
                                    if client_vip in ['VIP1', 'VIP2', 'VIP3', 'VIP4', 'VIP5', 'VIP6', 'VIP7', 'VIP8']:
                                        if vip_level == "Standard" or client_vip > vip_level:
                                            vip_level = client_vip
                                            print(f"DEBUG - Chambre {reservation['room_no']}: VIP mis à jour à {vip_level}")
                        except Exception as e:
                            print(f"DEBUG - Erreur client secondaire: {e}")
                    
                    # N'ajouter que si la chambre a des clients
                    if has_clients:
                        # Compter le nombre de clients
                        num_guests = 0
                        if reservation.get('client_principal_id'):
                            num_guests += 1
                        if reservation.get('client_secondaire_id'):
                            num_guests += 1
                        
                        occupied_rooms.append({
                            'room_no': reservation['room_no'],
                            'num_guests': num_guests,
                            'vip_level': vip_level,
                            'client_name': client_name
                        })
                        
                        print(f"DEBUG - Chambre {reservation['room_no']}: {num_guests} personne(s), {vip_level}, {client_name}")
            
            # Trier les chambres : VIP d'abord, puis Standard
            def sort_key(room):
                if room['vip_level'] == 'Standard':
                    return (1, room['room_no'])  # Standard en dernier, trié par numéro de chambre
                else:
                    # VIP en premier, triés par niveau VIP (VIP8 le plus important, VIP1 le moins)
                    vip_num = int(room['vip_level'].replace('VIP', ''))
                    return (0, -vip_num, room['room_no'])  # -vip_num pour trier VIP8 en premier
            
            occupied_rooms.sort(key=sort_key)
            
            print(f"DEBUG - Chambres occupées avec clients trouvées: {len(occupied_rooms)}")
            debug_order = [f"{r['room_no']}({r['vip_level']})" for r in occupied_rooms]
            print(f"DEBUG - Ordre de tri: {debug_order}")
            
            return jsonify(occupied_rooms)
        else:
            print("DEBUG - Aucune réservation trouvée")
            return jsonify([])
            
    except Exception as e:
        print(f"DEBUG - Erreur lors de la récupération des réservations: {e}")
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
        all_reservations = supabase.table('reservations').select('*').execute()
        
        reservations_data = all_reservations.data
        
        # 1. Arrivées aujourd'hui
        arrivees_aujourd_hui = len([r for r in reservations_data if r.get('arrival') == today])
        
        # 2. Départs aujourd'hui
        departs_aujourd_hui = len([r for r in reservations_data if r.get('departure') == today])
        
        # 3. Clients actuellement à l'hôtel (réservations en cours)
        reservations_actuelles = get_reservations_actuelles()
        clients_actuellement = len(reservations_actuelles)
        
        # 4. Chambres utilisées (nombre de chambres occupées)
        chambres_utilisees = len(set(r.get('room_no') for r in reservations_actuelles if r.get('room_no')))
        
        stats = {
            'arrivees_aujourd_hui': arrivees_aujourd_hui,
            'departs_aujourd_hui': departs_aujourd_hui,
            'clients_actuellement': clients_actuellement,
            'chambres_utilisees': chambres_utilisees
        }
        
        return stats
    except Exception as e:
        print(f"Erreur get_dashboard_stats: {str(e)}")
        return {}

def get_reservations_jour():
    """Récupérer les réservations du jour (arrivées)"""
    try:
        today = date.today().isoformat()
        result = supabase.table('reservations').select('*').eq('arrival', today).execute()
        
        # Filtrer pour exclure les réservations déjà validées
        filtered_reservations = []
        for reservation in result.data:
            statut = reservation.get('statut')
            # Inclure seulement futures et jour (pas encore validées comme arrivées)
            if statut in ['futures', 'jour']:
                filtered_reservations.append(reservation)
        
        return filtered_reservations
    except Exception as e:
        print(f"DEBUG - Erreur get_reservations_jour: {e}")
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
            # Récupérer chaque client individuellement pour éviter les problèmes de clé
            for client_id in client_ids:
                try:
                    client_result = supabase.table('clients').select('guest_name, guest_title').eq('id', client_id).execute()
                    if client_result.data:
                        clients_data[client_id] = client_result.data[0]

                except Exception as e:
                    print(f"DEBUG - Erreur client {client_id}: {e}")
        
        # Enrichir les réservations avec les données des clients
        for reservation in reservations:
            reservation['client_principal'] = clients_data.get(reservation.get('client_principal_id'))
            reservation['client_secondaire'] = clients_data.get(reservation.get('client_secondaire_id'))
        
        return reservations
    except Exception as e:
        pass
        return []

def get_departures_jour():
    """Récupérer les départs du jour"""
    try:
        today = date.today().isoformat()
        print(f"DEBUG - Date d'aujourd'hui: {today}")
        
        # Récupérer les réservations qui partent aujourd'hui
        result = supabase.table('reservations').select(
            'resv_name_id, room_no, departure, departure_time, client_principal_id, client_secondaire_id, statut, room_category_label'
        ).eq('departure', today).execute()
        
        print(f"DEBUG - Réservations avec departure = {today}: {len(result.data)}")
        
        # Filtrer pour inclure les réservations qui peuvent partir aujourd'hui
        departures = []
        print(f"DEBUG - Toutes les réservations trouvées: {len(result.data)}")
        
        for reservation in result.data:
            statut = reservation.get('statut')
            print(f"DEBUG - Réservation {reservation.get('resv_name_id')}: Statut = {statut}")
            
            # Inclure les réservations futures, en cours et jour (pas encore terminées)
            if statut in ['futures', 'en_cours', 'jour']:
                departures.append(reservation)
                print(f"DEBUG - Départ inclus: {reservation.get('resv_name_id')} - Statut: {statut} - Chambre: {reservation.get('room_no')}")
            else:
                print(f"DEBUG - Départ exclu: {reservation.get('resv_name_id')} - Statut: {statut} (exclu)")
        
        print(f"DEBUG - Départs trouvés pour aujourd'hui: {len(departures)}")
        return departures
    except Exception as e:
        print(f"DEBUG - Erreur get_departures_jour: {e}")
        return []

def get_departures_jour_with_clients():
    """Récupérer les départs du jour avec les informations des clients"""
    try:
        departures = get_departures_jour()
        
        if not departures:
            return []
        
        # Récupérer tous les IDs de clients en une seule fois
        client_ids = set()
        for departure in departures:
            if departure.get('client_principal_id'):
                client_ids.add(departure['client_principal_id'])
            if departure.get('client_secondaire_id'):
                client_ids.add(departure['client_secondaire_id'])
        
        # Récupérer tous les clients en une seule fois
        clients_data = {}
        if client_ids:
            # Récupérer chaque client individuellement pour éviter les problèmes de clé
            for client_id in client_ids:
                try:
                    client_result = supabase.table('clients').select('guest_name, guest_title').eq('id', client_id).execute()
                    if client_result.data:
                        clients_data[client_id] = client_result.data[0]
                except Exception as e:
                    print(f"Erreur récupération client {client_id}: {e}")
        
        # Enrichir et formater les départs
        formatted_departures = []
        for departure in departures:
            # Récupérer le nom du client principal
            client_name = "Client inconnu"
            if departure.get('client_principal_id') and departure['client_principal_id'] in clients_data:
                client_info = clients_data[departure['client_principal_id']]
                title = client_info.get('guest_title', '')
                name = client_info.get('guest_name', '')
                client_name = f"{title} {name}".strip() if title else name
            
            # Formater l'heure de départ
            departure_time = departure.get('departure_time', '')
            if departure_time:
                try:
                    # Convertir l'heure en format lisible
                    time_obj = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                    formatted_time = time_obj.strftime('%H:%M')
                except:
                    formatted_time = "Heure non définie"
            else:
                formatted_time = "Heure non définie"
            
            # Gérer la chambre (assignée ou non)
            room_no = departure.get('room_no', '')
            room_category = departure.get('room_category_label', '')
            
            if room_no and room_no.strip():
                room_display = f"Chambre {room_no}"
            elif room_category and room_category.strip():
                room_display = f"Catégorie {room_category}"
            else:
                room_display = "Chambre Non assignée"
            
            # Déterminer l'action appropriée selon le statut
            status = departure.get('statut', '')
            if status == 'futures':
                action_text = "Arrivée prévue"
            elif status == 'en_cours':
                action_text = "En séjour"
            elif status == 'jour':
                action_text = "Départ aujourd'hui"
            else:
                action_text = "Action"
            
            formatted_departure = {
                'resv_name_id': departure.get('resv_name_id'),
                'room_no': room_display,
                'departure_time': formatted_time,
                'client_name': client_name,
                'client_principal_id': departure.get('client_principal_id'),
                'client_secondaire_id': departure.get('client_secondaire_id'),
                'action_text': action_text,
                'status': status
            }
            
            formatted_departures.append(formatted_departure)

        
        return formatted_departures
    except Exception as e:
        print(f"DEBUG - Erreur get_departures_jour_with_clients: {e}")
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
    """Récupérer les réservations actuellement en cours avec clients actuels"""
    try:
        today = date.today().isoformat()
        
        # Récupérer UNIQUEMENT les réservations avec statut "en_cours"
        result = supabase.table('reservations').select('*').eq('statut', 'en_cours').gte('departure', today).execute()
        
        if not result.data:
            return []
        
        # Récupérer les IDs des clients de ces réservations
        client_ids = set()
        for res in result.data:
            if res.get('client_principal_id'):
                client_ids.add(res['client_principal_id'])
            if res.get('client_secondaire_id'):
                client_ids.add(res['client_secondaire_id'])
        
        # Vérifier que les clients ont bien le statut "actuel"
        if client_ids:
            clients_result = supabase.table('clients').select('id, statut').in_('id', list(client_ids)).execute()
            
            # Filtrer pour ne garder que les réservations avec clients "actuel"
            reservations_actuelles = []
            for res in result.data:
                has_actuel_client = False
                
                # Vérifier le client principal
                if res.get('client_principal_id'):
                    for client in clients_result.data:
                        if client['id'] == res['client_principal_id'] and client.get('statut') == 'actuel':
                            has_actuel_client = True
                            break
                
                # Vérifier le client secondaire
                if not has_actuel_client and res.get('client_secondaire_id'):
                    for client in clients_result.data:
                        if client['id'] == res['client_secondaire_id'] and client.get('statut') == 'actuel':
                            has_actuel_client = True
                            break
                
                # N'ajouter que si au moins un client a le statut "actuel"
                if has_actuel_client:
                    reservations_actuelles.append(res)
            
            return reservations_actuelles
        
        return []
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

@app.route('/api/reservations/<reservation_id>/status', methods=['PUT'])
def update_reservation_status(reservation_id):
    """Mettre à jour le statut d'une réservation"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Statut requis'}), 400
        
        # Vérifier que le statut est valide
        valid_statuses = ['futures', 'jour', 'en_cours', 'terminee']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'Statut invalide. Valeurs autorisées: {", ".join(valid_statuses)}'}), 400
        
        # Récupérer la réservation actuelle pour validation
        current_result = supabase.table('reservations').select('*').eq('resv_name_id', reservation_id).execute()
        if not current_result.data:
            return jsonify({'success': False, 'message': 'Réservation non trouvée'}), 404
        
        current_reservation = current_result.data[0]
        current_status = current_reservation.get('statut')
        today = datetime.now().date()
        
        # Validation des transitions de statut selon la logique métier
        if new_status == 'en_cours':
            # Peut passer à 'en_cours' seulement si c'est le jour d'arrivée ou après
            if current_reservation.get('arrival'):
                arrival_date = parse_date(current_reservation['arrival'])
                if arrival_date > today:
                    return jsonify({'success': False, 'message': 'Ne peut pas passer à "en_cours" avant l\'arrivée'}), 400
            else:
                return jsonify({'success': False, 'message': 'Date d\'arrivée non définie'}), 400
                
        elif new_status == 'terminee':
            # Peut passer à 'terminee' seulement si c'est le jour de départ ou après
            if current_reservation.get('departure'):
                departure_date = parse_date(current_reservation['departure'])
                if departure_date > today:
                    return jsonify({'success': False, 'message': 'Ne peut pas passer à "terminee" avant le départ'}), 400
            else:
                return jsonify({'success': False, 'message': 'Date de départ non définie'}), 400
        
        # Mettre à jour le statut de la réservation
        result = supabase.table('reservations').update({'statut': new_status}).eq('resv_name_id', reservation_id).execute()
        
        # Mettre à jour le statut des clients selon le nouveau statut de la réservation
        client_ids = []
        if current_reservation.get('client_principal_id'):
            client_ids.append(current_reservation['client_principal_id'])
        if current_reservation.get('client_secondaire_id'):
            client_ids.append(current_reservation['client_secondaire_id'])
        
        if client_ids:
            # Définir le statut client selon le statut de la réservation
            client_status = None
            
            if new_status == 'jour':
                client_status = 'arrive'  # Client arrivé
            elif new_status == 'en_cours':
                client_status = 'actuel'  # Client actuellement en séjour
            elif new_status == 'terminee':
                client_status = 'parti'  # Client parti
            
            # Mettre à jour le statut des clients
            if client_status:
                try:
                    supabase.table('clients').update({'statut': client_status}).in_('id', client_ids).execute()
                    print(f"DEBUG - Statut des clients mis à jour vers '{client_status}' pour les IDs: {client_ids}")
                except Exception as e:
                    print(f"DEBUG - Erreur lors de la mise à jour du statut des clients: {e}")
        
        # Vider le cache pour refléter les changements
        clear_cache()
        
        # Préparer le message de retour
        message = f'Statut de la réservation mis à jour vers {new_status}'
        if client_ids and client_status:
            message += f' et statut des clients mis à jour vers {client_status}'
        
        return jsonify({
            'success': True, 
            'message': message,
            'reservation_id': reservation_id,
            'new_status': new_status,
            'clients_updated': len(client_ids) if client_ids else 0,
            'client_status': client_status if client_ids else None
        })
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/test/chat')
def test_chat():
    """Page de test pour le chat bot"""
    return render_template('test_chat.html')

@app.route('/test/chat-gauche')
def test_chat_gauche():
    """Page de test pour le chat bot qui se déploie depuis la gauche"""
    return render_template('test_chat_gauche.html')

@app.route('/test/chat-droite-bas')
def test_chat_droite_bas():
    """Page de test pour le chat bot qui se déploie depuis la droite en bas"""
    return render_template('test_chat_droite.html')

# ===== CHATBOT AI API =====

@app.route('/api/chatbot/query', methods=['POST'])
@login_required
def chatbot_query():
    """API pour interroger le chatbot AI - Reproduction exacte du comportement mobile"""
    try:
        data = request.get_json()
        question = data.get('question', '').lower()
        user_id = session.get('user_id')
        
        if not question:
            return jsonify({'success': False, 'message': 'Question requise'}), 400
        
        print(f"🤖 Question reçue: '{question}' de l'utilisateur {user_id}")
        
        # ÉTAPE 2: Récupération Données Supabase (comme dans mobile)
        print("📊 Récupération du contexte hôtel...")
        
        # ÉTAPE 3: Construction du Contexte
        context_data = get_context_data_for_question(question)
        print(f"🏨 Contexte construit: {len(str(context_data))} caractères")
        
        # ÉTAPE 4: Envoi à OpenAI GPT-3.5
        print("🚀 Appel OpenAI GPT-3.5...")
        response = generate_ai_response(question, user_id)
        
        print(f"✅ Réponse IA générée: {len(response)} caractères")
        
        # ÉTAPE 5: Sauvegarde Interaction (CRITIQUE - manquait dans mobile!)
        print("💾 Sauvegarde dans ai_interactions...")
        save_ai_interaction(user_id, question, response, context_data)
        
        print("🎉 Interaction complète sauvegardée!")
        
        return jsonify({
            'success': True,
            'response': response,
            'question': question,
            'context_used': len(str(context_data))
        })
        
    except Exception as e:
        print(f"❌ Erreur chatbot: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

def generate_ai_response(question, user_id):
    """Générer une réponse AI basée sur la question et les données Supabase avec OpenAI GPT-3.5
    - Reproduction exacte du comportement mobile AIConciergeService"""
    
    try:
        # Récupérer le contexte des données Supabase (comme _getHotelContext() dans mobile)
        context_data = get_context_data_for_question(question)
        
        # Préparer le prompt pour OpenAI (IA omnisciente)
        system_prompt = """Tu es l'assistant concierge AYORA, un chatbot OMNISCIENT pour un hôtel de luxe en Thaïlande.

🎯 TON RÔLE : Tu as accès à TOUTES les données de l'hôtel et tu peux répondre à TOUTES les questions possibles.

📊 TES DONNÉES : Tu as accès à :
- Tous les clients (actuels, passés, futurs)
- Toutes les réservations et chambres
- Toutes les préférences et allergies
- Tous les niveaux VIP et statuts
- Tout le personnel et leur disponibilité
- Toutes les alertes et problèmes
- Toutes les statistiques et tendances
- Tout le calendrier et planning

🧠 TES CAPACITÉS :
- Analysez les données pour répondre précisément
- Faites des recommandations basées sur l'historique
- Identifiez des patterns et tendances
- Anticipez les besoins et problèmes
- Donnez des insights business

💬 STYLE DE RÉPONSE :
- Professionnel mais chaleureux
- Concis mais complet
- Basé sur les données réelles
- Avec des suggestions d'actions si pertinent
- Toujours en français

🚀 SOIS CRÉATIF : Tu peux répondre à des questions que personne n'a encore posées en analysant les données différemment.

💡 IMPORTANT : 
1. Réponds UNIQUEMENT à la question posée
2. Pour "bonjour", "salut", etc. → Salutation simple et chaleureuse
3. Pour les listes → Utilise des retours à la ligne et des puces
4. Ne donne des infos que si on te les demande explicitement

📝 FORMATAGE DES LISTES :
- Utilise des retours à la ligne pour chaque élément
- Ajoute des puces (-) pour chaque item
- Garde une structure claire et lisible
- IMPORTANT: Utilise \n pour les retours à la ligne, pas d'espaces multiples"""
        
        user_prompt = f"""Question du personnel: {question}

IMPORTANT: 
- Si c'est une salutation (bonjour, salut, etc.) → Réponds UNIQUEMENT par une salutation chaleureuse
- Si c'est une question spécifique → Utilise les données ci-dessous pour répondre précisément
- Pour les listes → Utilise des retours à la ligne (\n) et des puces (-)
- FORMATAGE OBLIGATOIRE: Chaque élément de liste doit être sur une nouvelle ligne

Données contextuelles disponibles (utilise-les SEULEMENT si nécessaire):
{context_data}

Réponds de manière claire, structurée et utile. Si tu n'as pas assez d'informations, dis-le poliment."""

        # Appeler OpenAI GPT-3.5 (API v1.0.0+)
        if openai_client:
            print(f"🚀 Appel OpenAI pour la question: '{question}'")
            
            # Construire l'historique des messages avec le contexte
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Ajouter l'historique des conversations précédentes
            conversation_history = get_conversation_history(user_id)
            if conversation_history:
                messages.extend(conversation_history)
                print(f"📚 Ajout de {len(conversation_history)} messages d'historique")
            
            # Ajouter la question actuelle
            messages.append({"role": "user", "content": user_prompt})
            
            response = openai_client.chat.completions.create(
                model=openai_model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"✅ Réponse OpenAI reçue: {len(ai_response)} caractères")
            
            # Améliorer le formatage de la réponse
            formatted_response = format_ai_response(ai_response, question)
            
            # Sauvegarder la conversation dans l'historique
            save_conversation_message(user_id, "user", question)
            save_conversation_message(user_id, "assistant", formatted_response)
            
            return formatted_response
        else:
            # Fallback vers les fonctions spécifiques si OpenAI n'est pas configuré
            print("⚠️ OpenAI non configuré, fallback vers fonctions spécifiques")
            return get_specific_response(question)
            
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        # En cas d'erreur, donner une réponse intelligente au lieu de bloquer
        return f"Je suis désolé, j'ai rencontré une erreur technique. Pouvez-vous reformuler votre question ? ({str(e)[:100]}...)"

def get_context_data_for_question(question):
    """Récupérer TOUTES les données contextuelles pour l'IA omnisciente"""
    context = {}
    
    try:
        print(f"🔍 Analyse de la question: '{question}'")
        question_lower = question.lower()
        
        # Récupérer TOUTES les données disponibles (pas seulement selon les mots-clés)
        print("📊 Récupération de toutes les données hôtel...")
        
        # 1. CLIENTS ET RÉSERVATIONS (données principales)
        context['clients_actuels'] = get_current_clients_info_raw()
        context['clients_tous'] = get_all_clients_info_raw()
        context['reservations_completes'] = get_all_reservations_info_raw()
        context['chambres_etat'] = get_rooms_status_raw()
        
        # 2. PRÉFÉRENCES ET BESOINS SPÉCIAUX
        context['preferences_alimentaires'] = get_allergies_info_raw()
        context['preferences_chambres'] = get_room_preferences_raw()
        context['demandes_speciales'] = get_special_requests_raw()
        
        # 3. VIP ET CLIENTÈLE
        context['clients_vip'] = get_vip_info_raw()
        context['statistiques_vip'] = get_vip_statistics_raw()
        
        # 4. ALERTES ET PROBLÈMES
        context['alertes'] = get_alerts_info_raw()
        context['problemes_actuels'] = get_current_issues_raw()
        
        # 5. PERSONNEL ET ÉQUIPES
        context['personnel'] = get_staff_info_raw()
        context['disponibilite_staff'] = get_staff_availability_raw()
        
        # 6. STATISTIQUES ET MÉTRIQUES
        context['statistiques_occupation'] = get_occupancy_statistics_raw()
        context['tendances_reservations'] = get_booking_trends_raw()
        
        # 7. CALENDRIER ET PLANNING
        context['calendrier_reservations'] = get_reservation_calendar_raw()
        context['evenements_speciaux'] = get_special_events_raw()
        
        print(f"✅ {len(context)} catégories de données récupérées")
        return format_context_for_openai(context)
        
    except Exception as e:
        print(f"❌ Erreur récupération contexte: {e}")
        return "Données non disponibles"

def format_context_for_openai(context):
    """Formater le contexte pour OpenAI"""
    formatted = ""
    
    if 'clients_actuels' in context:
        formatted += f"CLIENTS ACTUELS:\n{context['clients_actuels']}\n\n"
        
    if 'preferences_alimentaires' in context:
        formatted += f"PRÉFÉRENCES ALIMENTAIRES:\n{context['preferences_alimentaires']}\n\n"
        
    if 'clients_vip' in context:
        formatted += f"CLIENTS VIP:\n{context['clients_vip']}\n\n"
        
    if 'reservations' in context:
        formatted += f"RÉSERVATIONS:\n{context['reservations']}\n\n"
        
    if 'alertes' in context:
        formatted += f"ALERTES:\n{context['alertes']}\n\n"
        
    if 'personnel' in context:
        formatted += f"PERSONNEL:\n{context['personnel']}\n\n"
    
    return formatted



def get_specific_response(question):
    """Obtenir une réponse spécifique en utilisant les fonctions existantes (fallback intelligent)"""
    question_lower = question.lower()
    
    # Salutations et questions de base
    if any(word in question_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir', 'comment ça va', 'ça va']):
        return "Bonjour ! Je suis ravi de vous accueillir. Je suis votre assistant AYORA et je peux vous aider avec toutes les questions concernant l'hôtel. Que souhaitez-vous savoir ?"
    
    # Questions sur les clients actuels
    if any(word in question_lower for word in ['qui', 'client', 'actuel', 'hotel', 'présent']):
        return get_current_clients_info()
    
    # Questions sur les allergies
    elif any(word in question_lower for word in ['allergie', 'allergique', 'intolérance', 'préférence alimentaire']):
        return get_allergies_info()
    
    # Questions sur les VIP
    elif any(word in question_lower for word in ['vip', 'important', 'niveau']):
        return get_vip_info()
    
    # Questions sur les réservations
    elif any(word in question_lower for word in ['réservation', 'chambre', 'occupation', 'disponible']):
        return get_reservations_info()
    
    # Questions sur les alertes
    elif any(word in question_lower for word in ['alerte', 'urgence', 'problème', 'attention']):
        return get_alerts_info()
    
    # Questions sur le personnel
    elif any(word in question_lower for word in ['staff', 'personnel', 'employé', 'équipe']):
        return get_staff_info()
    
    # Questions générales
    elif any(word in question_lower for word in ['aide', 'comment', 'quoi', 'quoi faire']):
        return get_general_help()
    
    # Réponse par défaut plus intelligente
    else:
        return f"Je comprends votre question '{question}'. Laissez-moi analyser nos données pour vous donner la meilleure réponse possible. Pouvez-vous préciser ce que vous souhaitez savoir exactement ?"

def get_current_clients_info_raw():
    """Récupérer les données brutes sur les clients actuels pour OpenAI"""
    try:
        # Récupérer les réservations en cours
        result = supabase.table('reservations').select(
            'resv_name_id, room_no, room_category_label, adults, children, vip, client_principal_id, client_secondaire_id'
        ).eq('statut', 'en_cours').execute()
        
        if not result.data:
            return "Aucune réservation en cours"
        
        # Récupérer les informations des clients
        client_ids = []
        for res in result.data:
            if res.get('client_principal_id'):
                client_ids.append(res['client_principal_id'])
            if res.get('client_secondaire_id'):
                client_ids.append(res['client_secondaire_id'])
        
        if not client_ids:
            return "Aucune information client disponible"
        
        clients_result = supabase.table('clients').select(
            'id, guest_name, guest_title, vip, preferences_alimentaires, preferences_chambre'
        ).in_('id', list(set(client_ids))).execute()
        
        if not clients_result.data:
            return "Aucune information client disponible"
        
        # Retourner les données brutes structurées
        data = {
            'reservations_en_cours': len(result.data),
            'chambres': []
        }
        
        for res in result.data:
            room_data = {
                'chambre': res.get('room_no'),
                'categorie': res.get('room_category_label'),
                'adultes': res.get('adults'),
                'enfants': res.get('children'),
                'vip': res.get('vip'),
                'clients': []
            }
            
            # Trouver les clients de cette réservation
            for client in clients_result.data:
                if client['id'] in [res.get('client_principal_id'), res.get('client_secondaire_id')]:
                    client_data = {
                        'nom': client.get('guest_name'),
                        'titre': client.get('guest_title'),
                        'vip': client.get('vip'),
                        'preferences_alimentaires': client.get('preferences_alimentaires'),
                        'preferences_chambre': client.get('preferences_chambre')
                    }
                    room_data['clients'].append(client_data)
            
            data['chambres'].append(room_data)
        
        return str(data)
        
    except Exception as e:
        print(f"Erreur get_current_clients_info_raw: {e}")
        return "Erreur lors de la récupération des données"

def get_all_clients_info_raw():
    """Récupérer TOUS les clients (actuels, passés, futurs)"""
    try:
        result = supabase.table('clients').select('*').execute()
        return f"Total clients: {len(result.data)}" if result.data else "Aucun client"
    except Exception as e:
        print(f"Erreur get_all_clients_info_raw: {e}")
        return "Erreur récupération"

def get_all_reservations_info_raw():
    """Récupérer TOUTES les réservations"""
    try:
        result = supabase.table('reservations').select('*').execute()
        return f"Total réservations: {len(result.data)}" if result.data else "Aucune réservation"
    except Exception as e:
        print(f"Erreur get_all_reservations_info_raw: {e}")
        return "Erreur récupération"

def get_rooms_status_raw():
    """Récupérer l'état de toutes les chambres"""
    try:
        result = supabase.table('reservations').select('room_no, statut, arrival, departure').execute()
        return f"Chambres: {len(result.data)}" if result.data else "Aucune chambre"
    except Exception as e:
        print(f"Erreur get_rooms_status_raw: {e}")
        return "Erreur récupération"

def get_room_preferences_raw():
    """Récupérer toutes les préférences de chambres"""
    try:
        result = supabase.table('clients').select('guest_name, preferences_chambre').not_.is_('preferences_chambre', 'null').execute()
        return f"Préférences chambres: {len(result.data)}" if result.data else "Aucune préférence"
    except Exception as e:
        print(f"Erreur get_room_preferences_raw: {e}")
        return "Erreur récupération"

def get_special_requests_raw():
    """Récupérer toutes les demandes spéciales"""
    try:
        result = supabase.table('reservations').select('special_requests').not_.is_('special_requests', 'null').execute()
        return f"Demandes spéciales: {len(result.data)}" if result.data else "Aucune demande"
    except Exception as e:
        print(f"Erreur get_special_requests_raw: {e}")
        return "Erreur récupération"

def get_vip_statistics_raw():
    """Récupérer les statistiques VIP"""
    try:
        result = supabase.table('clients').select('vip').not_.is_('vip', 'null').execute()
        vip_counts = {}
        for client in result.data:
            vip = client.get('vip', 'Standard')
            vip_counts[vip] = vip_counts.get(vip, 0) + 1
        return f"Statistiques VIP: {vip_counts}"
    except Exception as e:
        print(f"Erreur get_vip_statistics_raw: {e}")
        return "Erreur récupération"

def get_current_issues_raw():
    """Récupérer les problèmes actuels"""
    try:
        # Simuler des problèmes basés sur les données
        return "Analyse des problèmes en cours..."
    except Exception as e:
        print(f"Erreur get_current_issues_raw: {e}")
        return "Erreur récupération"

def get_staff_availability_raw():
    """Récupérer la disponibilité du staff"""
    try:
        result = supabase.table('staff_directory').select('available, department').execute()
        available = sum(1 for staff in result.data if staff.get('available'))
        total = len(result.data)
        return f"Staff disponible: {available}/{total}"
    except Exception as e:
        print(f"Erreur get_staff_availability_raw: {e}")
        return "Erreur récupération"

def get_occupancy_statistics_raw():
    """Récupérer les statistiques d'occupation"""
    try:
        result = supabase.table('reservations').select('statut').execute()
        stats = {}
        for res in result.data:
            statut = res.get('statut', 'inconnu')
            stats[statut] = stats.get(statut, 0) + 1
        return f"Statistiques occupation: {stats}"
    except Exception as e:
        print(f"Erreur get_occupancy_statistics_raw: {e}")
        return "Erreur récupération"

def get_booking_trends_raw():
    """Récupérer les tendances de réservation"""
    try:
        result = supabase.table('reservations').select('arrival, departure').execute()
        return f"Tendances: {len(result.data)} réservations analysées"
    except Exception as e:
        print(f"Erreur get_booking_trends_raw: {e}")
        return "Erreur récupération"

def get_reservation_calendar_raw():
    """Récupérer le calendrier des réservations"""
    try:
        result = supabase.table('reservations').select('arrival, departure, room_no').execute()
        return f"Calendrier: {len(result.data)} dates"
    except Exception as e:
        print(f"Erreur get_reservation_calendar_raw: {e}")
        return "Erreur récupération"

def get_special_events_raw():
    """Récupérer les événements spéciaux"""
    try:
        # Simuler des événements spéciaux
        return "Événements: Analyse en cours..."
    except Exception as e:
        print(f"Erreur get_special_events_raw: {e}")
        return "Erreur récupération"

def get_current_clients_info():
    """Récupérer les informations sur les clients actuels (formaté pour l'affichage)"""
    try:
        # Récupérer les réservations en cours
        result = supabase.table('reservations').select(
            'resv_name_id, room_no, room_category_label, adults, children, vip, client_principal_id, client_secondaire_id'
        ).eq('statut', 'en_cours').execute()
        
        if not result.data:
            return "Aucun client n'est actuellement à l'hôtel."
        
        # Récupérer les informations des clients
        client_ids = []
        for res in result.data:
            if res.get('client_principal_id'):
                client_ids.append(res['client_principal_id'])
            if res.get('client_secondaire_id'):
                client_ids.append(res['client_secondaire_id'])
        
        if not client_ids:
            return "Aucune information client disponible."
        
        clients_result = supabase.table('clients').select(
            'id, guest_name, guest_title, vip, preferences_alimentaires, preferences_chambre'
        ).in_('id', list(set(client_ids))).execute()
        
        if not clients_result.data:
            return "Aucune information client disponible."
        
        # Formater la réponse
        response = f"Actuellement, {len(result.data)} chambre(s) sont occupées :\n\n"
        
        for res in result.data:
            room_info = f"🏨 Chambre {res.get('room_no', 'N/A')} ({res.get('room_category_label', 'Standard')})\n"
            
            # Trouver les clients de cette réservation
            room_clients = []
            for client in clients_result.data:
                if client['id'] in [res.get('client_principal_id'), res.get('client_secondaire_id')]:
                    client_name = f"{client.get('guest_title', '')} {client.get('guest_name', 'N/A')}".strip()
                    vip_info = f" (VIP{client.get('vip', 'Standard')})" if client.get('vip') else ""
                    room_clients.append(f"👤 {client_name}{vip_info}")
            
            response += room_info + "\n".join(room_clients) + "\n\n"
        
        return response.strip()
        
    except Exception as e:
        print(f"Erreur get_current_clients_info: {e}")
        return "Désolé, je ne peux pas récupérer les informations sur les clients actuels pour le moment."

def get_allergies_info_raw():
    """Récupérer les données brutes sur les allergies pour OpenAI"""
    try:
        result = supabase.table('clients').select(
            'guest_name, guest_title, preferences_alimentaires, preferences_opera'
        ).not_.is_('preferences_alimentaires', 'null').execute()
        
        if not result.data:
            return "Aucune préférence alimentaire enregistrée"
        
        data = []
        for client in result.data:
            client_data = {
                'nom': client.get('guest_name'),
                'titre': client.get('guest_title'),
                'preferences_alimentaires': client.get('preferences_alimentaires'),
                'preferences_opera': client.get('preferences_opera')
            }
            data.append(client_data)
        
        return str(data)
        
    except Exception as e:
        print(f"Erreur get_allergies_info_raw: {e}")
        return "Erreur lors de la récupération des données"

def get_allergies_info():
    """Récupérer les informations sur les allergies et préférences alimentaires (formaté pour l'affichage)"""
    try:
        # Récupérer les clients avec des préférences alimentaires
        result = supabase.table('clients').select(
            'guest_name, guest_title, preferences_alimentaires, preferences_opera'
        ).not_.is_('preferences_alimentaires', 'null').execute()
        
        if not result.data:
            return "Aucune information sur les allergies ou préférences alimentaires n'est disponible."
        
        response = "📋 Clients avec préférences alimentaires :\n\n"
        
        for client in result.data:
            client_name = f"{client.get('guest_title', '')} {client.get('guest_name', 'N/A')}".strip()
            preferences = client.get('preferences_alimentaires', 'Aucune préférence')
            
            response += f"👤 {client_name}\n"
            response += f"🍽️ {preferences}\n\n"
        
        return response.strip()
        
    except Exception as e:
        print(f"Erreur get_allergies_info: {e}")
        return "Désolé, je ne peux pas récupérer les informations sur les allergies pour le moment."

def get_vip_info_raw():
    """Récupérer les données brutes sur les VIP pour OpenAI"""
    try:
        result = supabase.table('clients').select(
            'guest_name, guest_title, vip, nombre_sejours'
        ).not_.is_('vip', 'null').execute()
        
        if not result.data:
            return "Aucun client VIP enregistré"
        
        data = []
        for client in result.data:
            client_data = {
                'nom': client.get('guest_name'),
                'titre': client.get('guest_title'),
                'vip': client.get('vip'),
                'nombre_sejours': client.get('nombre_sejours')
            }
            data.append(client_data)
        
        return str(data)
        
    except Exception as e:
        print(f"Erreur get_vip_info_raw: {e}")
        return "Erreur lors de la récupération des données"

def get_vip_info():
    """Récupérer les informations sur les clients VIP (formaté pour l'affichage)"""
    try:
        # Récupérer les clients VIP
        result = supabase.table('clients').select(
            'guest_name, guest_title, vip, nombre_sejours'
        ).not_.is_('vip', 'null').execute()
        
        if not result.data:
            return "Aucun client VIP n'est enregistré."
        
        # Grouper par niveau VIP
        vip_levels = {}
        for client in result.data:
            vip_level = client.get('vip', 'Standard')
            if vip_level not in vip_levels:
                vip_levels[vip_level] = []
            vip_levels[vip_level].append(client)
        
        response = "👑 Clients VIP :\n\n"
        
        # Trier par niveau VIP (VIP8 le plus élevé)
        for vip_level in sorted(vip_levels.keys(), key=lambda x: int(x.replace('VIP', '0')) if 'VIP' in str(x) else 0, reverse=True):
            clients = vip_levels[vip_level]
            response += f"🌟 {vip_level} ({len(clients)} client(s)):\n"
            
            for client in clients:
                client_name = f"{client.get('guest_title', '')} {client.get('guest_name', 'N/A')}".strip()
                sejours = client.get('nombre_sejours', 0)
                response += f"  👤 {client_name} ({sejours} séjour(s))\n"
            
            response += "\n"
        
        return response.strip()
        
    except Exception as e:
        print(f"Erreur get_vip_info: {e}")
        return "Désolé, je ne peux pas récupérer les informations VIP pour le moment."

def get_reservations_info_raw():
    """Récupérer les données brutes sur les réservations pour OpenAI"""
    try:
        result = supabase.table('reservations').select(
            'resv_name_id, room_no, arrival, departure, statut, adults, children, vip'
        ).in_('statut', ['en_cours', 'jour', 'futures']).execute()
        
        if not result.data:
            return "Aucune réservation active"
        
        data = {
            'total': len(result.data),
            'par_statut': {},
            'vip': []
        }
        
        for res in result.data:
            statut = res.get('statut', 'futures')
            if statut not in data['par_statut']:
                data['par_statut'][statut] = 0
            data['par_statut'][statut] += 1
            
            if res.get('vip'):
                vip_data = {
                    'chambre': res.get('room_no'),
                    'vip': res.get('vip'),
                    'arrivee': res.get('arrival'),
                    'depart': res.get('departure')
                }
                data['vip'].append(vip_data)
        
        return str(data)
        
    except Exception as e:
        print(f"Erreur get_reservations_info_raw: {e}")
        return "Erreur lors de la récupération des données"

def get_reservations_info():
    """Récupérer les informations sur les réservations (formaté pour l'affichage)"""
    try:
        # Récupérer les réservations actuelles et futures
        result = supabase.table('reservations').select(
            'resv_name_id, room_no, arrival, departure, statut, adults, children, vip'
        ).in_('statut', ['en_cours', 'jour', 'futures']).execute()
        
        if not result.data:
            return "Aucune réservation active n'est disponible."
        
        # Compter par statut
        stats = {'en_cours': 0, 'jour': 0, 'futures': 0}
        for res in result.data:
            statut = res.get('statut', 'futures')
            if statut in stats:
                stats[statut] += 1
        
        response = "📅 État des réservations :\n\n"
        response += f"🏨 En cours : {stats['en_cours']} chambre(s)\n"
        response += f"📥 Arrivées aujourd'hui : {stats['jour']} chambre(s)\n"
        response += f"📅 Futures : {stats['futures']} chambre(s)\n\n"
        
        # Détails des VIP
        vip_reservations = [res for res in result.data if res.get('vip')]
        if vip_reservations:
            response += "👑 Réservations VIP :\n"
            for res in vip_reservations[:5]:  # Limiter à 5
                response += f"  🏨 Chambre {res.get('room_no', 'N/A')} - {res.get('arrival')}\n"
        
        return response.strip()
        
    except Exception as e:
        print(f"Erreur get_reservations_info: {e}")
        return "Désolé, je ne peux pas récupérer les informations sur les réservations pour le moment."

def get_alerts_info_raw():
    """Récupérer les données brutes sur les alertes pour OpenAI"""
    try:
        result = supabase.table('ai_alerts').select(
            'alert_type, priority, title, message, room_number, created_at'
        ).eq('is_read', False).order('created_at', desc=True).execute()
        
        if not result.data:
            return "Aucune alerte active"
        
        data = []
        for alert in result.data[:10]:
            alert_data = {
                'type': alert.get('alert_type'),
                'priorite': alert.get('priority'),
                'titre': alert.get('title'),
                'message': alert.get('message'),
                'chambre': alert.get('room_number'),
                'cree_le': alert.get('created_at')
            }
            data.append(alert_data)
        
        return str(data)
        
    except Exception as e:
        print(f"Erreur get_alerts_info_raw: {e}")
        return "Erreur lors de la récupération des données"

def get_alerts_info():
    """Récupérer les informations sur les alertes (formaté pour l'affichage)"""
    try:
        # Récupérer les alertes non lues
        result = supabase.table('ai_alerts').select(
            'alert_type, priority, title, message, room_number, created_at'
        ).eq('is_read', False).order('created_at', desc=True).execute()
        
        if not result.data:
            return "Aucune alerte active n'est disponible."
        
        response = "🚨 Alertes actives :\n\n"
        
        for alert in result.data[:10]:  # Limiter à 10 alertes
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            priority_icon = priority_emoji.get(alert.get('priority', 'low'), '⚪')
            
            response += f"{priority_icon} {alert.get('title', 'Sans titre')}\n"
            response += f"   📍 Chambre: {alert.get('room_number', 'N/A')}\n"
            response += f"   📝 {alert.get('message', 'Aucun message')}\n"
            response += f"   ⏰ {alert.get('created_at', 'N/A')}\n\n"
        
        return response.strip()
        
    except Exception as e:
        print(f"Erreur get_alerts_info: {e}")
        return "Désolé, je ne peux pas récupérer les informations sur les alertes pour le moment."

def get_staff_info_raw():
    """Récupérer les données brutes sur le personnel pour OpenAI"""
    try:
        result = supabase.table('staff_directory').select(
            'first_name, last_name, position, department, available, status'
        ).execute()
        
        if not result.data:
            return "Aucune information sur le personnel"
        
        data = {
            'total': len(result.data),
            'par_departement': {}
        }
        
        for staff in result.data:
            dept = staff.get('department', 'Autre')
            if dept not in data['par_departement']:
                data['par_departement'][dept] = []
            
            staff_data = {
                'nom': f"{staff.get('first_name', '')} {staff.get('last_name', '')}".strip(),
                'position': staff.get('position'),
                'disponible': staff.get('available'),
                'statut': staff.get('status')
            }
            data['par_departement'][dept].append(staff_data)
        
        return str(data)
        
    except Exception as e:
        print(f"Erreur get_staff_info_raw: {e}")
        return "Erreur lors de la récupération des données"

def get_staff_info():
    """Récupérer les informations sur le personnel (formaté pour l'affichage)"""
    try:
        # Récupérer le personnel disponible
        result = supabase.table('staff_directory').select(
            'first_name, last_name, position, department, available, status'
        ).execute()
        
        if not result.data:
            return "Aucune information sur le personnel n'est disponible."
        
        response = "👥 Personnel :\n\n"
        
        # Grouper par département
        departments = {}
        for staff in result.data:
            dept = staff.get('department', 'Autre')
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(staff)
        
        for dept, staff_list in departments.items():
            response += f"🏢 {dept}:\n"
            for staff in staff_list:
                name = f"{staff.get('first_name', '')} {staff.get('last_name', '')}".strip()
                position = staff.get('position', 'N/A')
                status = "🟢 Disponible" if staff.get('available') else "🔴 Indisponible"
                
                response += f"  👤 {name} - {position} - {status}\n"
            response += "\n"
        
        return response.strip()
        
    except Exception as e:
        print(f"Erreur get_staff_info: {e}")
        return "Désolé, je ne peux pas récupérer les informations sur le personnel pour le moment."

def get_general_help():
    """Aide générale pour le chatbot"""
    return """🤖 Assistant AYORA - Aide générale

Voici ce que je peux vous dire :

👥 **Clients actuels** : "Qui est à l'hôtel ?", "Quels clients sont présents ?"
🍽️ **Allergies** : "Y a-t-il des allergies ?", "Préférences alimentaires ?"
👑 **VIP** : "Quels sont les clients VIP ?", "Niveaux VIP ?"
📅 **Réservations** : "État des réservations ?", "Chambres occupées ?"
🚨 **Alertes** : "Y a-t-il des alertes ?", "Problèmes actuels ?"
👥 **Personnel** : "Qui est disponible ?", "Équipe actuelle ?"

Posez-moi une question spécifique !"""

def save_ai_interaction(user_id, question, response, context_data=None):
    """Sauvegarder l'interaction AI dans la base - Reproduction exacte du mobile"""
    try:
        # Calculer le temps de réponse (simulation pour l'instant)
        response_time_ms = 500  # 500ms par défaut
        
        # Préparer les données comme dans le cahier des charges
        interaction_data = {
            'staff_user_id': user_id,
            'question': question,
            'ai_response': response,
            'context_data': {
                'source': 'web_chatbot',
                'hotel_context': context_data,
                'timestamp': datetime.now().isoformat()
            },
            'response_time_ms': response_time_ms,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"💾 Données à sauvegarder: {len(str(interaction_data))} caractères")
        
        # INSERT INTO ai_interactions (comme dans le flux mobile)
        result = supabase.table('ai_interactions').insert(interaction_data).execute()
        
        if result.data:
            print(f"✅ Interaction sauvegardée avec ID: {result.data[0].get('id', 'N/A')}")
        else:
            print("⚠️ Aucune donnée retournée après sauvegarde")
            
    except Exception as e:
        print(f"❌ Erreur sauvegarde interaction: {e}")
        # Ne pas faire échouer la requête si la sauvegarde échoue

def get_conversation_history(user_id, limit=10):
    """Récupérer l'historique des conversations pour un utilisateur"""
    try:
        # Récupérer les dernières interactions
        result = supabase.table('ai_interactions')\
            .select('question, ai_response')\
            .eq('staff_user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        if result.data:
            # Convertir en format OpenAI (alternance user/assistant)
            messages = []
            for interaction in reversed(result.data):  # Inverser pour avoir l'ordre chronologique
                if interaction.get('question'):
                    messages.append({"role": "user", "content": interaction['question']})
                if interaction.get('ai_response'):
                    messages.append({"role": "assistant", "content": interaction['ai_response']})
            
            print(f"📚 Historique récupéré: {len(messages)} messages")
            return messages
        else:
            print("📚 Aucun historique trouvé")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'historique: {e}")
        return []

def save_conversation_message(user_id, role, content):
    """Sauvegarder un message de conversation pour l'historique"""
    try:
        # Créer une interaction temporaire pour l'historique
        data = {
            'id': str(uuid.uuid4()),
            'staff_user_id': user_id,
            'question': content if role == 'user' else '',
            'ai_response': content if role == 'assistant' else '',
            'context_data': {'role': role, 'conversation': True},
            'response_time_ms': 0,
            'created_at': datetime.now().isoformat()
        }
        
        # Insérer dans Supabase
        result = supabase.table('ai_interactions').insert(data).execute()
        
        if result.data:
            print(f"💬 Message {role} sauvegardé dans l'historique")
            return True
        else:
            print(f"❌ Échec de la sauvegarde du message {role}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du message {role}: {e}")
        return False

def format_ai_response(response, question):
    """Améliorer le formatage de la réponse AI"""
    try:
        # Si c'est une salutation simple, ne pas la modifier
        question_lower = question.lower()
        if any(word in question_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir', 'comment ça va', 'ça va']):
            return response
        
        # Améliorer le formatage des listes et des retours à la ligne
        lines = response.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Si c'est un élément de liste sans tiret, en ajouter un
                if not line.startswith('-') and not line.startswith('•') and not line.startswith('*'):
                    # Vérifier si c'est un élément de liste (contient des informations structurées)
                    if any(char in line for char in ['VIP', 'Chambre', 'Client', 'Réservation', 'Room', 'Guest']):
                        formatted_lines.append(f"- {line}")
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
                
                # Ajouter un retour à la ligne après chaque élément de liste
                if line.startswith('-') and i < len(lines) - 1:
                    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    if next_line and not next_line.startswith('-'):
                        formatted_lines.append("")  # Ligne vide pour séparer
        
        # Nettoyer les lignes vides multiples
        result = '\n'.join(formatted_lines)
        result = '\n'.join(line for line in result.split('\n') if line.strip() or line == "")
        
        print(f"🔧 Réponse formatée: {len(result.split(chr(10)))} lignes")
        return result
        
    except Exception as e:
        print(f"❌ Erreur lors du formatage de la réponse: {e}")
        return response

@app.route('/debug/rooms')
def debug_rooms():
    """Page de debug pour tester l'API des chambres"""
    return render_template('debug_rooms.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
