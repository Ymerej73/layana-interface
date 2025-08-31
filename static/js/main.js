// Main JavaScript file for Layana Hotel Management System

// Variables globales
let currentClientId = null;
let currentQuickEditField = null;
let currentTheme = localStorage.getItem('theme') || 'light';
let searchTimeout = null;
let chatMessages = []; // Historique des messages du chat
let chatOpen = false; // État d'ouverture du chat

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    loadSettings();
    initializeEventListeners();
    initializeSearchDebouncing();
    initializeCalendar();
    initializeRoomsStatus();
    
    // Initialiser le chat si l'élément existe
    if (document.getElementById('chat-widget')) {
        initializeChat();
        initializeChatEventListeners();
    }
});

// Initialisation des écouteurs d'événements
function initializeEventListeners() {
    // Quick edit modal
    const quickEditModal = document.getElementById('quick-edit-modal');
    if (quickEditModal) {
        quickEditModal.addEventListener('click', function(e) {
            if (e.target === quickEditModal) {
                closeQuickEditModal();
            }
        });
    }
    
    // Quick edit form
    const quickEditForm = document.getElementById('quick-edit-form');
    if (quickEditForm) {
        quickEditForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveQuickEdit();
        });
    }
}

// Debouncing pour la recherche
function initializeSearchDebouncing() {
    const searchInputs = document.querySelectorAll('.search-input input[name="search"]');
    searchInputs.forEach(input => {
        // Empêcher la soumission automatique du formulaire
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performManualSearch();
            }
        });
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const inputValue = this.value; // Capturer la valeur avant le setTimeout
            
            // Ne pas déclencher la recherche si moins de 2 caractères
            if (inputValue.length < 2) {
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(inputValue);
            }, 1000); // 1 seconde de délai pour laisser le temps de taper
        });
    });
}

// Fonction de recherche optimisée
function performSearch(query) {
    // Vérifier que query n'est pas undefined ou null
    if (query === undefined || query === null) {
        query = '';
    }
    
    // Construire l'URL de recherche
    const currentUrl = new URL(window.location);
    if (query.trim() === '') {
        currentUrl.searchParams.delete('search');
    } else {
        currentUrl.searchParams.set('search', query.trim());
    }
    currentUrl.searchParams.set('page', '1'); // Reset à la première page
    
    // Naviguer vers la nouvelle URL
    window.location.href = currentUrl.toString();
}

// Fonction de recherche manuelle (bouton)
function performManualSearch() {
    const searchInput = document.querySelector('.search-input input[name="search"]');
    if (searchInput) {
        performSearch(searchInput.value);
    }
}

// Variables globales pour le calendrier
let currentCalendarYear = new Date().getFullYear();
let currentCalendarMonth = new Date().getMonth() + 1;

// Initialisation du calendrier amélioré
function initializeCalendar() {
    loadCalendarData();
}

// Gérer les clics sur la modal
function handleModalClick(event) {
    if (event.target.id === 'guests-modal') {
        closeGuestsModal();
    }
}

// Fermer la modal des clients
function closeGuestsModal() {
    const modal = document.getElementById('guests-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }
}

// Voir les détails d'un client
function viewClientDetails(clientId) {
    if (clientId) {
        window.location.href = `/client/${clientId}`;
    }
}

// Gestion du sélecteur de langue
function toggleLanguageMenu() {
    const languageMenu = document.getElementById('language-menu');
    if (languageMenu) {
        languageMenu.classList.toggle('show');
    }
}

// Gestion du menu des notifications
function toggleNotificationsMenu() {
    const notificationsMenu = document.getElementById('notifications-menu');
    if (notificationsMenu) {
        notificationsMenu.classList.toggle('show');
    }
}

// Fermer les menus en cliquant à l'extérieur
document.addEventListener('click', function(event) {
    const languageSelector = document.querySelector('.language-selector');
    const languageMenu = document.getElementById('language-menu');
    const notificationsContainer = document.querySelector('.notifications');
    const notificationsMenu = document.getElementById('notifications-menu');
    
    // Fermer le menu de langue
    if (languageSelector && languageMenu && !languageSelector.contains(event.target)) {
        languageMenu.classList.remove('show');
    }
    
    // Fermer le menu des notifications
    if (notificationsContainer && notificationsMenu && !notificationsContainer.contains(event.target)) {
        notificationsMenu.classList.remove('show');
    }
});

// Fonction pour définir le thème depuis les paramètres
function setTheme(theme) {
    currentTheme = theme;
    document.body.classList.toggle('dark-theme', theme === 'dark');
    localStorage.setItem('theme', theme);
    
    // Mettre à jour les boutons de sélection
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.theme === theme) {
            btn.classList.add('active');
        }
    });
    
    // Mettre à jour l'icône du bouton dans la navbar
    const themeToggle = document.querySelector('.theme-btn i');
    if (themeToggle) {
        themeToggle.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    showToast(`Thème ${theme === 'dark' ? 'sombre' : 'clair'} activé`);
}

// Fonction pour définir le thème sans afficher de toast
function setThemeSilent(theme) {
    currentTheme = theme;
    document.body.classList.toggle('dark-theme', theme === 'dark');
    localStorage.setItem('theme', theme);
    
    // Mettre à jour les boutons de sélection
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.theme === theme) {
            btn.classList.add('active');
        }
    });
    
    // Mettre à jour l'icône du bouton dans la navbar
    const themeToggle = document.querySelector('.theme-btn i');
    if (themeToggle) {
        themeToggle.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    // Pas de toast ici
}

// Fonction pour définir la langue
function setLanguage(language) {
    // Sauvegarder la préférence
    localStorage.setItem('language', language);
    
    // Envoyer la préférence au serveur
    fetch('/api/settings/language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: language })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`Langue changée vers ${language === 'fr' ? 'Français' : 'English'}`);
            // Recharger la page pour appliquer les changements
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showToast('Erreur lors du changement de langue');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('Erreur lors du changement de langue');
    });
}

// Fonction pour basculer les notifications
function toggleNotifications(enabled) {
    localStorage.setItem('notifications', enabled);
    showToast(`Notifications ${enabled ? 'activées' : 'désactivées'}`);
}

// Fonction pour basculer les notifications email
function toggleEmailNotifications(enabled) {
    localStorage.setItem('emailNotifications', enabled);
    showToast(`Notifications email ${enabled ? 'activées' : 'désactivées'}`);
}

// Fonction pour définir la densité d'affichage
function setDensity(density) {
    localStorage.setItem('density', density);
    document.body.classList.toggle('compact-mode', density === 'compact');
    showToast(`Densité d'affichage changée vers ${density === 'compact' ? 'compact' : 'confortable'}`);
}

// Fonction pour définir la densité d'affichage sans afficher de toast
function setDensitySilent(density) {
    localStorage.setItem('density', density);
    document.body.classList.toggle('compact-mode', density === 'compact');
    // Pas de toast ici
}

// Fonction pour basculer les animations
function toggleAnimations(enabled) {
    localStorage.setItem('animations', enabled);
    document.body.classList.toggle('no-animations', !enabled);
    showToast(`Animations ${enabled ? 'activées' : 'désactivées'}`);
}

// Fonction pour basculer la sauvegarde automatique
function toggleAutoSave(enabled) {
    localStorage.setItem('autoSave', enabled);
    showToast(`Sauvegarde automatique ${enabled ? 'activée' : 'désactivée'}`);
}

// Fonction pour sauvegarder tous les paramètres
function saveSettings() {
    const settings = {
        theme: currentTheme,
        language: document.getElementById('language-selector').value,
        notifications: document.getElementById('notifications-toggle').checked,
        emailNotifications: document.getElementById('email-notifications-toggle').checked,
        density: document.getElementById('density-selector').value,
        animations: document.getElementById('animations-toggle').checked,
        autoSave: document.getElementById('auto-save-toggle').checked
    };
    
    localStorage.setItem('userSettings', JSON.stringify(settings));
    
    // Envoyer les paramètres au serveur
    fetch('/api/settings/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Paramètres sauvegardés avec succès');
        } else {
            showToast('Erreur lors de la sauvegarde');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('Erreur lors de la sauvegarde');
    });
}

// Fonction pour réinitialiser les paramètres
function resetSettings() {
    if (confirm('Êtes-vous sûr de vouloir réinitialiser tous les paramètres ?')) {
        localStorage.removeItem('userSettings');
        localStorage.removeItem('theme');
        localStorage.removeItem('language');
        localStorage.removeItem('notifications');
        localStorage.removeItem('emailNotifications');
        localStorage.removeItem('density');
        localStorage.removeItem('animations');
        localStorage.removeItem('autoSave');
        
        // Recharger la page
        window.location.reload();
    }
}

// Fonction pour charger les paramètres au démarrage
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('userSettings') || '{}');
    
    // Appliquer le thème
    if (settings.theme) {
        setTheme(settings.theme);
    }
    
    // Appliquer la densité
    if (settings.density) {
        document.body.classList.toggle('compact-mode', settings.density === 'compact');
    }
    
    // Appliquer les animations
    if (settings.animations !== undefined) {
        document.body.classList.toggle('no-animations', !settings.animations);
    }
    
    // Mettre à jour les contrôles sur la page des paramètres
    if (window.location.pathname === '/settings') {
        updateSettingsControls(settings);
    }
}

// Fonction pour mettre à jour les contrôles des paramètres
function updateSettingsControls(settings) {
    // Thème
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.theme === settings.theme) {
            btn.classList.add('active');
        }
    });
    
    // Langue
    const languageSelector = document.getElementById('language-selector');
    if (languageSelector && settings.language) {
        languageSelector.value = settings.language;
    }
    
    // Notifications
    const notificationsToggle = document.getElementById('notifications-toggle');
    if (notificationsToggle) {
        notificationsToggle.checked = settings.notifications || false;
    }
    
    // Notifications email
    const emailNotificationsToggle = document.getElementById('email-notifications-toggle');
    if (emailNotificationsToggle) {
        emailNotificationsToggle.checked = settings.emailNotifications || false;
    }
    
    // Densité
    const densitySelector = document.getElementById('density-selector');
    if (densitySelector && settings.density) {
        densitySelector.value = settings.density;
    }
    
    // Animations
    const animationsToggle = document.getElementById('animations-toggle');
    if (animationsToggle) {
        animationsToggle.checked = settings.animations !== false;
    }
    
    // Sauvegarde automatique
    const autoSaveToggle = document.getElementById('auto-save-toggle');
    if (autoSaveToggle) {
        autoSaveToggle.checked = settings.autoSave !== false;
    }
}

function loadTheme() {
    document.body.classList.toggle('dark-theme', currentTheme === 'dark');
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Mettre à jour l'icône du bouton
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

// Fonctions de navigation optimisées
function viewArrivalDetails(reservationId) {
    window.location.href = `/reservation/${reservationId}`;
}

function viewRoomDetails(reservationId) {
    window.location.href = `/reservation/${reservationId}`;
}

function viewReservation(reservationId) {
    window.location.href = `/reservation/${reservationId}`;
}

function editReservation(reservationId) {
    // Fonctionnalité à implémenter
    showToast('Fonctionnalité d\'édition de réservation en cours de développement');
}

function changeRoom(reservationId) {
    // Fonctionnalité à implémenter
    showToast('Fonctionnalité de changement de chambre en cours de développement');
}

function viewClient(clientId) {
    window.location.href = `/client/${clientId}`;
}

function editClient(clientId) {
    // Fonctionnalité à implémenter
    showToast('Fonctionnalité d\'édition de client en cours de développement');
}

function showAddClientModal() {
    // Fonctionnalité à implémenter
    showToast('Fonctionnalité d\'ajout de client en cours de développement');
}

function closeClientModal() {
    // Fonctionnalité à implémenter
    showToast('Fonctionnalité de fermeture de modal en cours de développement');
}

// Fonctions de rafraîchissement optimisées
function refreshClients() {
    window.location.reload();
}

function refreshReservations() {
    window.location.reload();
}

function refreshClientsActuels() {
    window.location.reload();
}

function refreshArrivals() {
    window.location.reload();
}

// Variables globales pour la vue actuelle
let currentView = 'arrivals';
let departuresData = [];

// Fonction pour basculer entre arrivées et départs
function switchView(view) {
    currentView = view;
    
    // Mettre à jour les boutons
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    
    // Mettre à jour le titre de la section
    const sectionTitle = document.getElementById('section-title');
    if (sectionTitle) {
        sectionTitle.textContent = view === 'arrivals' ? 'Arrivées Aujourd\'hui' : 'Départs Aujourd\'hui';
    }
    
    // Basculer entre les vues
    document.querySelectorAll('.view-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (view === 'arrivals') {
        document.getElementById('arrivals-view').classList.add('active');
    } else {
        document.getElementById('departures-view').classList.add('active');
        loadDeparturesData();
    }
}

// Fonction pour charger les données de départs
async function loadDeparturesData() {
    try {
        const response = await fetch('/api/departures/today');
        if (response.ok) {
            departuresData = await response.json();
            renderDepartures();
        } else {
            console.error('Erreur lors du chargement des départs');
            showEmptyDeparturesState();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des départs:', error);
        showEmptyDeparturesState();
    }
}

// Fonction pour afficher les départs
function renderDepartures() {
    const departuresContainer = document.querySelector('.departures-list');
    if (!departuresContainer) return;
    
    if (departuresData.length === 0) {
        showEmptyDeparturesState();
        return;
    }
    
    departuresContainer.innerHTML = departuresData.map(departure => `
        <div class="departure-item clickable" onclick="viewDepartureDetails('${departure.resv_name_id}')" style="margin: 0 16px 8px 16px !important; max-width: calc(100% - 32px) !important;">
            <div class="departure-info">
                <div class="guest-name">
                    ${departure.client_principal?.guest_name || `Réservation ${departure.resv_name_id}`}
                </div>
                <div class="departure-details">
                    <span class="room-number">
                        <i class="fas fa-door-open"></i>
                        Chambre ${departure.room_no || 'Non assignée'}
                    </span>
                    <span class="departure-time">
                        <i class="fas fa-clock"></i>
                        ${departure.departure_time || 'Heure non définie'}
                    </span>
                </div>
            </div>
            <div class="departure-status">
                <div class="status-controls">
                    ${departure.statut === 'futures' ? 
                        `<div class="status-info">
                            <i class="fas fa-clock"></i>
                            <span>Arrivée prévue</span>
                        </div>` : ''
                    }
                    ${departure.statut === 'jour' ? 
                        `<button class="btn-status btn-status-info" onclick="changeReservationStatus('${departure.resv_name_id}', 'en_cours')" title="Client installé à l'hôtel">
                            <i class="fas fa-bed"></i> En séjour
                        </button>` : ''
                    }
                    ${departure.statut === 'en_cours' ? 
                        `<button class="btn-status btn-status-warning" onclick="changeReservationStatus('${departure.resv_name_id}', 'terminee')" title="Client parti de l'hôtel">
                            <i class="fas fa-sign-out-alt"></i> Départ
                        </button>` : ''
                    }
                </div>
                <span class="status-badge status-${departure.statut || 'unknown'}">
                    ${(departure.statut || 'unknown').charAt(0).toUpperCase() + (departure.statut || 'unknown').slice(1)}
                </span>
                <i class="fas fa-chevron-right departure-arrow"></i>
            </div>
        </div>
    `).join('');
}

// Fonction pour afficher l'état vide des départs
function showEmptyDeparturesState() {
    const departuresContainer = document.querySelector('.departures-list');
    if (departuresContainer) {
        departuresContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-times"></i>
                <p>Aucun départ prévu aujourd'hui</p>
            </div>
        `;
    }
}

// Fonction pour rafraîchir la vue actuelle
function refreshCurrentView() {
    if (currentView === 'arrivals') {
        refreshArrivals();
    } else {
        loadDeparturesData();
    }
}

// Fonction pour voir les détails d'un départ
function viewDepartureDetails(reservationId) {
    // Rediriger vers la page de détail de la réservation
    window.location.href = `/reservation/${reservationId}`;
}

// Fonctions d'ajout d'informations client
function addEmail(clientId) {
    openQuickEditModal(clientId, 'email', '');
}

function addPhone(clientId) {
    openQuickEditModal(clientId, 'telephone', '');
}

// Fonctions de modal manquantes
function closeReservationModal() {
    showToast('Fonctionnalité en cours de développement');
}

function closeRoomChangeModal() {
    showToast('Fonctionnalité en cours de développement');
}

function closeRoomMapModal() {
    showToast('Fonctionnalité en cours de développement');
}

function closeSearchModal() {
    showToast('Fonctionnalité en cours de développement');
}

function saveClient() {
    showToast('Fonctionnalité en cours de développement');
}

function saveReservation() {
    showToast('Fonctionnalité en cours de développement');
}

function saveRoomChange() {
    showToast('Fonctionnalité en cours de développement');
}

function showAddReservationModal() {
    showToast('Fonctionnalité en cours de développement');
}

function showSearchModal() {
    showToast('Fonctionnalité en cours de développement');
}

function switchTab(tabName) {
    showToast('Fonctionnalité en cours de développement');
}

// Fonctions de pagination optimisées
function goToPage(page) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('page', page);
    window.location.href = currentUrl.toString();
}

function nextPage() {
    const currentPage = parseInt(document.querySelector('.pagination .active')?.textContent || '1');
    const totalPages = parseInt(document.querySelector('.pagination-info')?.textContent.match(/(\d+)/)?.[1] || '1');
    if (currentPage < totalPages) {
        goToPage(currentPage + 1);
    }
}

function prevPage() {
    const currentPage = parseInt(document.querySelector('.pagination .active')?.textContent || '1');
    if (currentPage > 1) {
        goToPage(currentPage - 1);
    }
}

// Fonctions de modal optimisées
function openQuickEditModal(clientId, field, currentValue) {
    currentClientId = clientId;
    currentQuickEditField = field;
    
    const modal = document.getElementById('quick-edit-modal');
    const input = document.getElementById('quick-edit-input');
    const label = document.getElementById('quick-edit-label');
    
            if (modal && input && label) {
            input.value = currentValue || '';
            label.textContent = `Modifier ${field === 'email' ? 'l\'email' : 'le téléphone'}`;
            modal.classList.add('show');
            input.focus();
        }
}

function closeQuickEditModal() {
    const modal = document.getElementById('quick-edit-modal');
    if (modal) {
        modal.classList.remove('show');
    }
    currentClientId = null;
    currentQuickEditField = null;
}

// Fonction de sauvegarde optimisée
function saveQuickEdit() {
    const value = document.getElementById('quick-edit-input').value;
    
    if (!value.trim()) {
        showToast('Veuillez saisir une valeur');
        return;
    }
    
    if (!currentClientId || !currentQuickEditField) {
        showToast('Erreur: données manquantes');
        return;
    }
    
    const data = { [currentQuickEditField]: value };
    
    showLoading();
    
    fetch(`/api/client/${currentClientId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        return response.json();
    })
    .then(result => {
        hideLoading();
        if (result.success) {
            showToast('Modification enregistrée');
            closeQuickEditModal();
            // Rafraîchir la page pour afficher les changements
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showToast(`Erreur: ${result.message}`);
        }
    })
    .catch(error => {
        hideLoading();
        showToast(`Erreur de connexion: ${error.message}`);
    });
}

// Fonctions d'affichage optimisées
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Supprimer les toasts existants
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(t => t.remove());
    
    document.body.appendChild(toast);
    
    // Animation d'entrée
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto-suppression
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function showLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.style.display = 'flex';
    }
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.style.display = 'none';
    }
}













// Export des fonctions pour utilisation dans les templates
window.loadTheme = loadTheme;
window.viewArrivalDetails = viewArrivalDetails;
window.viewRoomDetails = viewRoomDetails;
window.viewReservation = viewReservation;
window.editReservation = editReservation;
window.changeRoom = changeRoom;
window.viewClient = viewClient;
window.editClient = editClient;
window.showAddClientModal = showAddClientModal;
window.closeClientModal = closeClientModal;
window.refreshClients = refreshClients;
window.refreshReservations = refreshReservations;
window.refreshClientsActuels = refreshClientsActuels;
window.refreshArrivals = refreshArrivals;
window.addEmail = addEmail;
window.addPhone = addPhone;
window.closeReservationModal = closeReservationModal;
window.closeRoomChangeModal = closeRoomChangeModal;
window.closeRoomMapModal = closeRoomMapModal;
window.closeSearchModal = closeSearchModal;
window.saveClient = saveClient;
window.saveReservation = saveReservation;
window.saveRoomChange = saveRoomChange;
window.showAddReservationModal = showAddReservationModal;
window.showSearchModal = showSearchModal;
window.switchTab = switchTab;
window.previousMonth = previousMonth;
window.goToPage = goToPage;
window.nextPage = nextPage;
window.prevPage = prevPage;
window.openQuickEditModal = openQuickEditModal;
window.closeQuickEditModal = closeQuickEditModal;
window.saveQuickEdit = saveQuickEdit;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;


// Export des fonctions de paramètres
window.setTheme = setTheme;
window.setLanguage = setLanguage;
window.toggleNotifications = toggleNotifications;
window.toggleEmailNotifications = toggleEmailNotifications;
window.setDensity = setDensity;
window.toggleAnimations = toggleAnimations;
window.toggleAutoSave = toggleAutoSave;
window.saveSettings = saveSettings;
window.resetSettings = resetSettings;
window.loadSettings = loadSettings;



// Initialisation de l'état des chambres
function initializeRoomsStatus() {
    loadRoomsStatus();
    // Recharger l'état des chambres toutes les 2 minutes
    setInterval(loadRoomsStatus, 120000);
}

// Chargement de l'état des chambres
async function loadRoomsStatus() {
    try {
        console.log('Chargement de l\'état des chambres...');
        
        // Afficher le chargement
        showRoomsLoading();
        
        const response = await fetch('/api/rooms/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const rooms = await response.json();
        console.log('Données des chambres reçues:', rooms);
        
        if (Array.isArray(rooms) && rooms.length > 0) {
            displayRoomsList(rooms);
        } else {
            showNoRooms();
        }
        
    } catch (error) {
        console.error('Erreur lors du chargement des chambres:', error);
        showRoomsError();
    }
}

// Fonctions d'affichage des chambres
function showRoomsLoading() {
    const loadingElement = document.getElementById('rooms-loading');
    const roomsListElement = document.getElementById('rooms-list');
    const noRoomsElement = document.getElementById('no-rooms');
    
    if (loadingElement) loadingElement.style.display = 'flex';
    if (roomsListElement) roomsListElement.style.display = 'none';
    if (noRoomsElement) noRoomsElement.style.display = 'none';
}

function displayRoomsList(rooms) {
    const loadingElement = document.getElementById('rooms-loading');
    const roomsListElement = document.getElementById('rooms-list');
    const noRoomsElement = document.getElementById('no-rooms');
    
    if (loadingElement) loadingElement.style.display = 'none';
    if (noRoomsElement) noRoomsElement.style.display = 'none';
    
    if (roomsListElement) {
        roomsListElement.style.display = 'flex';
        roomsListElement.innerHTML = '';
        
        rooms.forEach(room => {
            const roomElement = createRoomElement(room);
            roomsListElement.appendChild(roomElement);
        });
    }
}

function createRoomElement(room) {
    const roomElement = document.createElement('div');
    roomElement.className = 'room-item';
    roomElement.onclick = () => viewRoomDetails(room.reservation_id);
    
    // Déterminer la classe CSS pour le niveau VIP
    let vipClass = 'vip-standard';
    if (room.vip_level && room.vip_level !== 'Standard') {
        if (room.vip_level.includes('VIP1')) vipClass = 'vip-vip1';
        else if (room.vip_level.includes('VIP2')) vipClass = 'vip-vip2';
        else if (room.vip_level.includes('VIP3')) vipClass = 'vip-vip3';
        else if (room.vip_level.includes('VIP4')) vipClass = 'vip-vip4';
        else if (room.vip_level.includes('VIP5')) vipClass = 'vip-vip5';
        else if (room.vip_level.includes('VIP6')) vipClass = 'vip-vip6';
        else if (room.vip_level.includes('VIP7')) vipClass = 'vip-vip7';
        else if (room.vip_level.includes('VIP8')) vipClass = 'vip-vip8';
    }
    
    roomElement.innerHTML = `
        <div class="room-header">
            <span class="room-number">Chambre ${room.room_no}</span>
            <span class="vip-badge ${vipClass}">${room.vip_level}</span>
        </div>
        <div class="room-details">
            <span class="client-name">${room.client_name}</span>
            <span class="guests-count">
                <i class="fas fa-users"></i>
                ${room.num_guests} personne${room.num_guests > 1 ? 's' : ''}
            </span>
        </div>
        <div class="room-click-hint">Cliquez pour voir les détails</div>
    `;
    
    return roomElement;
}

function showNoRooms() {
    const loadingElement = document.getElementById('rooms-loading');
    const roomsListElement = document.getElementById('rooms-list');
    const noRoomsElement = document.getElementById('no-rooms');
    
    if (loadingElement) loadingElement.style.display = 'none';
    if (roomsListElement) roomsListElement.style.display = 'none';
    if (noRoomsElement) noRoomsElement.style.display = 'flex';
}

function showRoomsError() {
    const loadingElement = document.getElementById('rooms-loading');
    const roomsListElement = document.getElementById('rooms-list');
    const noRoomsElement = document.getElementById('no-rooms');
    
    if (loadingElement) loadingElement.style.display = 'none';
    if (roomsListElement) roomsListElement.style.display = 'none';
    if (noRoomsElement) {
        noRoomsElement.style.display = 'flex';
        noRoomsElement.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <p>Erreur lors du chargement des chambres</p>
            <button onclick="loadRoomsStatus()" class="btn btn-secondary">Réessayer</button>
        `;
    }
}

// Rafraîchir l'état des chambres
function refreshRoomsStatus() {
    const button = event.target.closest('button');
    if (button) {
        const icon = button.querySelector('i');
        icon.classList.add('fa-spin');
        
        loadRoomsStatus().finally(() => {
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        });
    }
}

// Fonction pour voir les détails d'une chambre
function viewRoomDetails(reservationId) {
    // Rediriger vers la page de détail de la réservation
    window.location.href = `/reservation/${reservationId}`;
}

// Fonctions d'affichage des chambres
function showRoomsLoading() {
    const loadingElement = document.getElementById('rooms-loading');
    const roomsListElement = document.getElementById('rooms-list');
    const noRoomsElement = document.getElementById('no-rooms');
    
    if (loadingElement) loadingElement.style.display = 'flex';
    if (roomsListElement) roomsListElement.style.display = 'none';
    if (noRoomsElement) noRoomsElement.style.display = 'none';
}



// Calendrier amélioré
function initializeCalendar() {
    loadCalendarData();
}

async function loadCalendarData() {
    try {
        console.log(`Chargement du calendrier pour ${currentCalendarYear}/${currentCalendarMonth}`);
        const response = await fetch(`/api/calendar/${currentCalendarYear}/${currentCalendarMonth}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Données du calendrier reçues:', data);
        
        renderCalendar(data);
        updateCalendarHeader();
        
        // Ajouter un message de confirmation
        console.log('Calendrier chargé avec succès');
    } catch (error) {
        console.error('Erreur lors du chargement du calendrier:', error);
        // Afficher un message d'erreur dans le calendrier
        const calendarContainer = document.getElementById('calendar-widget-large');
        if (calendarContainer) {
            calendarContainer.innerHTML = `
                <div class="calendar-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Erreur lors du chargement du calendrier</p>
                    <button onclick="loadCalendarData()" class="btn btn-secondary">Réessayer</button>
                </div>
            `;
        }
    }
}

function renderCalendar(data) {
    const calendarContainer = document.getElementById('calendar-widget-large');
    if (!calendarContainer) return;
    
    const calendar = generateCalendarHTML(data);
    calendarContainer.innerHTML = calendar;
}

function generateCalendarHTML(data) {
    const year = data.year;
    const month = data.month;
    const calendarData = data.calendar_data || {};
    
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);
    const startDate = new Date(firstDay);
    
    // Calculer le jour de la semaine (0 = dimanche, 1 = lundi, etc.)
    let dayOfWeek = firstDay.getDay();
    // Convertir pour que lundi = 0, mardi = 1, ..., dimanche = 6
    dayOfWeek = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
    
    // Reculer au lundi de la semaine qui contient le premier jour du mois
    startDate.setDate(firstDay.getDate() - dayOfWeek);
    
    console.log('Date de début du calendrier:', startDate.toISOString().split('T')[0], 'Jour de la semaine:', startDate.getDay());
    
    let calendarHTML = `
        <div class="calendar-header">
            <div>Lun</div><div>Mar</div><div>Mer</div><div>Jeu</div><div>Ven</div><div>Sam</div><div>Dim</div>
        </div>
        <div class="calendar-grid">
    `;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    for (let i = 0; i < 42; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        
        // Formater la date en YYYY-MM-DD pour la clé
        const year = currentDate.getFullYear();
        const month = String(currentDate.getMonth() + 1).padStart(2, '0');
        const day = String(currentDate.getDate()).padStart(2, '0');
        const dateKey = `${year}-${month}-${day}`;
        const dayData = calendarData[dateKey] || { arrivals: [], departures: [], guests: [] };
        
        const isToday = currentDate.getTime() === today.getTime();
        const isCurrentMonth = currentDate.getMonth() === month - 1;
        const hasEvents = dayData.arrivals && dayData.arrivals.length > 0 || 
                         dayData.departures && dayData.departures.length > 0;
        
        let dayClass = 'calendar-day';
        if (!isCurrentMonth) dayClass += ' other-month';
        if (isToday) dayClass += ' today';
        if (hasEvents) dayClass += ' has-events';
        
        // Debug: vérifier que la date correspond
        if (currentDate.getDate() === 22 && currentDate.getMonth() === 7) { // 22 août (mois 7 = août)
            console.log('Date 22 août trouvée:', dateKey, 'Jour affiché:', currentDate.getDate(), 'Index:', i);
        }
        
        calendarHTML += `
            <div class="${dayClass}" onclick="showDayDetails('${dateKey}')" style="cursor: pointer;" data-date="${dateKey}" data-day="${currentDate.getDate()}">
                <div class="day-number">${currentDate.getDate()}</div>
                ${hasEvents ? `<div class="day-events">
                    ${dayData.arrivals && dayData.arrivals.length > 0 ? `<div class="event-dot arrival"></div>` : ''}
                    ${dayData.departures && dayData.departures.length > 0 ? `<div class="event-dot departure"></div>` : ''}
                </div>` : ''}
            </div>
        `;
    }
    
    calendarHTML += '</div>';
    return calendarHTML;
}

function updateCalendarHeader() {
    const monthElement = document.getElementById('current-month');
    if (monthElement) {
        const monthNames = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ];
        monthElement.textContent = `${monthNames[currentCalendarMonth - 1]} ${currentCalendarYear}`;
    }
}

function previousMonth() {
    currentCalendarMonth--;
    if (currentCalendarMonth < 1) {
        currentCalendarMonth = 12;
        currentCalendarYear--;
    }
    loadCalendarData();
}

function nextMonth() {
    currentCalendarMonth++;
    if (currentCalendarMonth > 12) {
        currentCalendarMonth = 1;
        currentCalendarYear++;
    }
    loadCalendarData();
}

async function showDayDetails(date) {
    try {
        console.log('showDayDetails appelé avec la date:', date);
        console.log('Date reçue:', date);
        console.log('Date parsée:', new Date(date));
        console.log('Date locale:', new Date(date).toLocaleDateString('fr-FR'));
        
        // Récupérer les données du calendrier pour cette date
        const response = await fetch(`/api/calendar/${currentCalendarYear}/${currentCalendarMonth}`);
        const data = await response.json();
        
        console.log('Données du calendrier reçues:', data);
        console.log('Données pour la date', date, ':', data.calendar_data[date]);
        
        const dayData = data.calendar_data[date] || { arrivals: [], departures: [], guests: [] };
        
        // Formater la date
        const dateObj = new Date(date);
        const dateStr = dateObj.toLocaleDateString('fr-FR', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        // Créer le contenu HTML pour le panneau
        let detailsHTML = `
            <div class="day-details-header">
                <h4><i class="fas fa-calendar-day"></i> ${dateStr}</h4>
            </div>
        `;
        
        // Section Arrivées
        if (dayData.arrivals && dayData.arrivals.length > 0) {
            detailsHTML += `
                <div class="activity-section">
                    <h4 class="activity-title arrival-title">
                        <i class="fas fa-sign-in-alt"></i> Arrivées (${dayData.arrivals.length})
                    </h4>
                    <div class="guests-list">
            `;
            
            dayData.arrivals.forEach(guest => {
                detailsHTML += `
                    <div class="guest-item arrival-item" onclick="viewReservation('${guest.reservation_id}')">
                        <div class="guest-info">
                            <div class="guest-name">${guest.client_name}</div>
                            <div class="guest-room">Chambre ${guest.room_no}</div>
                        </div>
                        <div class="guest-actions">
                            <i class="fas fa-chevron-right"></i>
                        </div>
                    </div>
                `;
            });
            
            detailsHTML += `
                    </div>
                </div>
            `;
        }
        
        // Section Départs
        if (dayData.departures && dayData.departures.length > 0) {
            detailsHTML += `
                <div class="activity-section">
                    <h4 class="activity-title departure-title">
                        <i class="fas fa-sign-out-alt"></i> Départs (${dayData.departures.length})
                    </h4>
                    <div class="guests-list">
            `;
            
            dayData.departures.forEach(guest => {
                detailsHTML += `
                    <div class="guest-item departure-item" onclick="viewReservation('${guest.reservation_id}')">
                        <div class="guest-info">
                            <div class="guest-name">${guest.client_name}</div>
                            <div class="guest-room">Chambre ${guest.room_no}</div>
                        </div>
                        <div class="guest-actions">
                            <i class="fas fa-chevron-right"></i>
                        </div>
                    </div>
                `;
            });
            
            detailsHTML += `
                    </div>
                </div>
            `;
        }
        

        
        // Si aucune activité
        if ((!dayData.arrivals || dayData.arrivals.length === 0) && 
            (!dayData.departures || dayData.departures.length === 0)) {
            detailsHTML += `
                <div class="empty-day">
                    <i class="fas fa-calendar-times"></i>
                    <p>Aucune activité prévue pour cette journée</p>
                    <p><small>Date sélectionnée: ${date}</small></p>
                </div>
            `;
        }
        
        // Mettre à jour le contenu du panneau
        const detailsContent = document.getElementById('day-details-content');
        if (detailsContent) {
            detailsContent.innerHTML = detailsHTML;
            console.log('Contenu du panneau mis à jour avec succès');
        } else {
            console.error('Panneau de détails non trouvé');
        }
        
        console.log('showDayDetails terminé avec succès');
        
    } catch (error) {
        console.error('Erreur lors du chargement des détails:', error);
        showToast('Erreur lors du chargement des détails de la journée');
    }
}

// Fermer le panneau de détails
function closeDayDetails() {
    const detailsContent = document.getElementById('day-details-content');
    if (detailsContent) {
        detailsContent.innerHTML = `
            <div class="day-details-placeholder">
                <i class="fas fa-calendar-plus"></i>
                <p>Sélectionnez une date dans le calendrier pour voir les détails</p>
            </div>
        `;
    }
}

// Export des nouvelles fonctions
window.previousMonth = previousMonth;
window.nextMonth = nextMonth;
window.showDayDetails = showDayDetails;
window.closeDayDetails = closeDayDetails;
window.switchView = switchView;
window.refreshCurrentView = refreshCurrentView;
window.viewDepartureDetails = viewDepartureDetails;

// ===== FONCTIONS POUR LA PAGE DES PARAMÈTRES =====

// Fonction pour définir le thème
function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.body.className = theme === 'dark' ? 'dark-theme' : '';
    localStorage.setItem('theme', theme);
    
    // Mettre à jour l'état actif des boutons de thème (seulement s'ils existent)
    const themeOptions = document.querySelectorAll('.theme-option-modern');
    if (themeOptions.length > 0) {
        themeOptions.forEach(btn => {
            btn.classList.remove('active');
        });
        const activeThemeBtn = document.querySelector(`[data-theme="${theme}"]`);
        if (activeThemeBtn) {
            activeThemeBtn.classList.add('active');
        }
    }
    
    // Afficher une notification
    showToast(`Thème ${theme === 'dark' ? 'sombre' : 'clair'} activé`);
    
    // Mettre à jour l'icône du thème dans le header si elle existe
    const headerThemeToggle = document.getElementById('theme-toggle');
    if (headerThemeToggle) {
        const icon = headerThemeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

// Fonction pour définir la langue
function setLanguage(language) {
    // Rediriger vers la route de changement de langue
    window.location.href = `/change-language/${language}`;
}

// Fonction pour définir la densité d'affichage
function setDensity(density) {
    // Mettre à jour l'état actif des options de densité (seulement si elles existent)
    const densityOptions = document.querySelectorAll('.density-option');
    if (densityOptions.length > 0) {
        densityOptions.forEach(option => {
            option.classList.remove('active');
        });
        const activeDensityOption = document.querySelector(`[data-density="${density}"]`);
        if (activeDensityOption) {
            activeDensityOption.classList.add('active');
        }
    }
    
    // Sauvegarder dans le localStorage
    localStorage.setItem('density', density);
    
    // Appliquer la densité (exemple)
    if (density === 'compact') {
        document.body.classList.add('compact-mode');
    } else {
        document.body.classList.remove('compact-mode');
    }
    
    showToast(`Mode ${density === 'compact' ? 'compact' : 'confortable'} activé`);
}

// Fonction pour activer/désactiver les notifications
function toggleNotifications(enabled) {
    if (enabled) {
        // Demander la permission pour les notifications
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    showToast('Notifications push activées');
                } else {
                    showToast('Permission refusée pour les notifications');
                    // Remettre le toggle à false
                    document.getElementById('notifications-toggle').checked = false;
                }
            });
        } else {
            showToast('Notifications non supportées par ce navigateur');
            document.getElementById('notifications-toggle').checked = false;
        }
    } else {
        showToast('Notifications push désactivées');
    }
    
    // Sauvegarder la préférence
    localStorage.setItem('notifications', enabled);
}

// Fonction pour activer/désactiver les notifications email
function toggleEmailNotifications(enabled) {
    localStorage.setItem('emailNotifications', enabled);
    showToast(`Notifications email ${enabled ? 'activées' : 'désactivées'}`);
}

// Fonction pour activer/désactiver les animations
function toggleAnimations(enabled) {
    if (enabled) {
        document.body.classList.remove('no-animations');
        showToast('Animations activées');
    } else {
        document.body.classList.add('no-animations');
        showToast('Animations désactivées');
    }
    
    localStorage.setItem('animations', enabled);
}

// Fonction pour activer/désactiver la sauvegarde automatique
function toggleAutoSave(enabled) {
    localStorage.setItem('autoSave', enabled);
    showToast(`Sauvegarde automatique ${enabled ? 'activée' : 'désactivée'}`);
}

// Fonction pour sauvegarder tous les paramètres
function saveSettings() {
    // Collecter tous les paramètres
    const settings = {
        theme: currentTheme,
        language: document.querySelector('.language-option .checkmark.active')?.parentElement.dataset.lang || 'fr',
        density: document.querySelector('.density-option .checkmark.active')?.parentElement.dataset.density || 'comfortable',
        notifications: document.getElementById('notifications-toggle')?.checked || false,
        emailNotifications: document.getElementById('email-notifications-toggle')?.checked || false,
        animations: document.getElementById('animations-toggle')?.checked || true,
        autoSave: document.getElementById('auto-save-toggle')?.checked || true
    };
    
    // Sauvegarder dans le localStorage
    Object.entries(settings).forEach(([key, value]) => {
        localStorage.setItem(key, value);
    });
    
    // Afficher une notification de succès
    showToast('Paramètres sauvegardés avec succès !', 'success');
    
    // Optionnel : envoyer au serveur
    // saveSettingsToServer(settings);
}

// Fonction pour réinitialiser les paramètres
function resetSettings() {
    // Afficher le modal de confirmation
    const modal = document.getElementById('reset-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Fonction pour fermer le modal de réinitialisation
function closeResetModal() {
    const modal = document.getElementById('reset-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Fonction pour confirmer la réinitialisation
function confirmReset() {
    // Réinitialiser tous les paramètres aux valeurs par défaut
    const defaultSettings = {
        theme: 'light',
        language: 'fr',
        density: 'comfortable',
        notifications: false,
        emailNotifications: false,
        animations: true,
        autoSave: true
    };
    
    // Appliquer les paramètres par défaut
    Object.entries(defaultSettings).forEach(([key, value]) => {
        localStorage.setItem(key, value);
    });
    
    // Appliquer le thème par défaut
    setTheme('light');
    
    // Remettre tous les toggles à leur état par défaut
    if (document.getElementById('notifications-toggle')) {
        document.getElementById('notifications-toggle').checked = false;
    }
    if (document.getElementById('email-notifications-toggle')) {
        document.getElementById('email-notifications-toggle').checked = false;
    }
    if (document.getElementById('animations-toggle')) {
        document.getElementById('animations-toggle').checked = true;
    }
    if (document.getElementById('auto-save-toggle')) {
        document.getElementById('auto-save-toggle').checked = true;
    }
    
    // Mettre à jour l'état actif des options
    updateActiveStates();
    
    // Fermer le modal
    closeResetModal();
    
    // Afficher une notification
    showToast('Paramètres réinitialisés aux valeurs par défaut', 'success');
}

// Fonction pour mettre à jour les états actifs
function updateActiveStates() {
    // Mettre à jour le thème actif
    document.querySelectorAll('.theme-option-modern').forEach(btn => {
        btn.classList.remove('active');
    });
    const currentThemeBtn = document.querySelector(`[data-theme="${currentTheme}"]`);
    if (currentThemeBtn) {
        currentThemeBtn.classList.add('active');
    }
    
    // Mettre à jour la langue active
    document.querySelectorAll('.language-option .checkmark').forEach(checkmark => {
        checkmark.classList.remove('active');
    });
    const currentLang = localStorage.getItem('language') || 'fr';
    const currentLangOption = document.querySelector(`[data-lang="${currentLang}"] .checkmark`);
    if (currentLangOption) {
        currentLangOption.classList.add('active');
    }
    
    // Mettre à jour la densité active
    document.querySelectorAll('.density-option .checkmark').forEach(checkmark => {
        checkmark.classList.remove('active');
    });
    const currentDensity = localStorage.getItem('density') || 'comfortable';
    const currentDensityOption = document.querySelector(`[data-density="${currentDensity}"] .checkmark`);
    if (currentDensityOption) {
        currentDensityOption.classList.add('active');
    }
}

// Fonction pour charger les paramètres
function loadSettings() {
    // Charger le thème (sans afficher le toast)
    const savedTheme = localStorage.getItem('theme') || 'light';
    setThemeSilent(savedTheme);
    
    // Charger la densité (sans afficher le toast)
    const savedDensity = localStorage.getItem('density') || 'comfortable';
    setDensitySilent(savedDensity);
    
    // Charger les autres paramètres
    const notifications = localStorage.getItem('notifications') === 'true';
    const emailNotifications = localStorage.getItem('emailNotifications') === 'true';
    const animations = localStorage.getItem('animations') !== 'false'; // true par défaut
    const autoSave = localStorage.getItem('autoSave') !== 'false'; // true par défaut
    
    // Appliquer les paramètres aux toggles
    if (document.getElementById('notifications-toggle')) {
        document.getElementById('notifications-toggle').checked = notifications;
    }
    if (document.getElementById('email-notifications-toggle')) {
        document.getElementById('email-notifications-toggle').checked = emailNotifications;
    }
    if (document.getElementById('animations-toggle')) {
        document.getElementById('animations-toggle').checked = animations;
    }
    if (document.getElementById('auto-save-toggle')) {
        document.getElementById('auto-save-toggle').checked = autoSave;
    }
    
    // Appliquer les animations
    if (!animations) {
        document.body.classList.add('no-animations');
    }
    
    // Mettre à jour les états actifs
    updateActiveStates();
}

// Export des fonctions des paramètres
window.setTheme = setTheme;
window.setThemeSilent = setThemeSilent;
window.setLanguage = setLanguage;
window.setDensity = setDensity;
window.setDensitySilent = setDensitySilent;
window.toggleNotifications = toggleNotifications;
window.toggleEmailNotifications = toggleEmailNotifications;
window.toggleAnimations = toggleAnimations;
window.toggleAutoSave = toggleAutoSave;
window.saveSettings = saveSettings;
window.resetSettings = resetSettings;
window.closeResetModal = closeResetModal;
window.confirmReset = confirmReset;

// Export des fonctions principales du dashboard
window.initializeCalendar = initializeCalendar;
window.loadCalendarData = loadCalendarData;
window.renderCalendar = renderCalendar;
window.generateCalendarHTML = generateCalendarHTML;
window.previousMonth = previousMonth;
window.nextMonth = nextMonth;
window.showDayDetails = showDayDetails;
window.closeDayDetails = closeDayDetails;
window.initializeRoomsStatus = initializeRoomsStatus;
window.refreshRoomsStatus = refreshRoomsStatus;
window.loadRoomsStatus = loadRoomsStatus;
window.viewRoomDetails = viewRoomDetails;
window.switchView = switchView;
window.refreshCurrentView = refreshCurrentView;
window.viewDepartureDetails = viewDepartureDetails;
window.showToast = showToast;
window.loadTheme = loadTheme;

// Export des fonctions du header
window.toggleLanguageMenu = toggleLanguageMenu;
window.toggleNotificationsMenu = toggleNotificationsMenu;

// Fonction pour changer le statut d'une réservation
async function changeReservationStatus(reservationId, newStatus) {
    try {
        const response = await fetch(`/api/reservations/${reservationId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(result.message, 'success');
            
            // Rafraîchir les données du dashboard si on est sur le dashboard
            if (typeof currentView !== 'undefined') {
                if (currentView === 'arrivals') {
                    refreshArrivals();
                } else if (currentView === 'departures') {
                    loadDeparturesData();
                }
                
                // Rafraîchir aussi l'état des chambres
                if (typeof refreshRoomsStatus === 'function') {
                    refreshRoomsStatus();
                }
            }
            
            // Si on est sur la page de détail, rafraîchir la page
            if (window.location.pathname.includes('/reservation/')) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            
        } else {
            const error = await response.json();
            showToast(`Erreur: ${error.message}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors du changement de statut:', error);
        showToast('Erreur lors du changement de statut', 'error');
    }
}

// Export de la fonction
window.changeReservationStatus = changeReservationStatus;

// ===== CHAT BOT FUNCTIONS =====

// Variables globales pour le chat
let chatBotResponses = {
    'gestion réservations': 'Pour gérer les réservations, allez dans l\'onglet "Réservations" depuis le menu principal. Vous pourrez voir toutes les réservations, les filtrer et modifier leurs statuts.',
    'clients actuels': 'Les clients actuels sont visibles dans l\'onglet "Clients Actuels". Cette section affiche uniquement les chambres occupées avec des clients en séjour.',
    'changement statut': 'Pour changer le statut d\'une réservation : 1) Allez sur le dashboard, 2) Dans "Arrivées et Départs Aujourd\'hui", cliquez sur "En séjour" ou "Départ" selon le cas, 3) Le statut se met à jour automatiquement.',
    'réservations': 'Les réservations peuvent avoir 4 statuts : futures, jour (arrivée), en_cours (client installé), terminee (client parti). Seuls les changements manuels sont possibles.',
    'vip': 'Les clients VIP sont classés par niveau de VIP1 à VIP8. VIP8 est le niveau le plus élevé. Ils apparaissent en premier dans l\'état des chambres.',
    'chambres': 'L\'état des chambres affiche uniquement les chambres actuellement occupées avec des clients en séjour. Les chambres vides ne sont pas affichées.',
    'dashboard': 'Le dashboard centralise toutes les informations importantes : arrivées/départs du jour, état des chambres, et permet de gérer les statuts des réservations.',
    'aide': 'Je peux vous aider avec : la gestion des réservations, les clients actuels, les changements de statut, les niveaux VIP, l\'état des chambres, et le dashboard. Que souhaitez-vous savoir ?'
};

// Initialisation du chat
function initializeChat() {
    console.log('Initialisation du chat...');
    console.log('chatMessages avant init:', chatMessages);
    
    // Vérifier que chatMessages est bien un tableau
    if (!Array.isArray(chatMessages)) {
        console.error('chatMessages n\'est pas un tableau, réinitialisation...');
        chatMessages = [];
    }
    
    // Définir l'heure du message de bienvenue
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('bot-welcome-time').textContent = timeString;
    
    // Ajouter le message de bienvenue à l'historique
    try {
        chatMessages.push({
            type: 'bot',
            text: 'Bonjour ! Je suis votre assistant AYORA. Comment puis-je vous aider aujourd\'hui ?',
            time: timeString
        });
        console.log('Message de bienvenue ajouté, taille chatMessages:', chatMessages.length);
    } catch (error) {
        console.error('Erreur lors de l\'ajout du message de bienvenue:', error);
    }
}

// Initialiser les écouteurs d'événements du chat
function initializeChatEventListeners() {
    // Écouteur pour la touche Entrée
    const chatInput = document.getElementById('chat-input-field');
    if (chatInput) {
        chatInput.addEventListener('keypress', handleChatInputKeyPress);
        console.log('Écouteur Entrée ajouté au chat');
    }
    
    // Écouteur pour le bouton d'envoi
    const sendButton = document.querySelector('.send-button');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
        console.log('Écouteur clic ajouté au bouton d\'envoi');
    }
    
    console.log('Chat event listeners initialisés avec succès');
}

// Ouvrir/Fermer le chat
function toggleChat() {
    const chatWidget = document.getElementById('chat-widget');
    const chatToggle = document.querySelector('.chat-toggle-floating');
    
    if (chatOpen) {
        // Fermer le chat
        chatWidget.classList.add('closing');
        setTimeout(() => {
            chatWidget.classList.remove('open', 'closing');
            chatOpen = false;
        }, 300);
        
        // Changer l'icône
        chatToggle.innerHTML = '<i class="fas fa-chevron-left"></i>';
        chatToggle.title = 'Ouvrir le chat';
    } else {
        // Ouvrir le chat
        chatWidget.classList.add('open');
        chatOpen = true;
        
        // Changer l'icône
        chatToggle.innerHTML = '<i class="fas fa-chevron-right"></i>';
        chatToggle.title = 'Masquer le chat';
        
        // Focus sur l'input
        document.getElementById('chat-input-field').focus();
    }
}

// Fermer complètement le chat
function closeChat() {
    const chatWidget = document.getElementById('chat-widget');
    const chatToggle = document.querySelector('.chat-toggle-floating');
    
    chatWidget.classList.add('closing');
    setTimeout(() => {
        chatWidget.classList.remove('open', 'closing');
        chatOpen = false;
    }, 300);
    
    // Remettre l'icône originale
    chatToggle.innerHTML = '<i class="fas fa-chevron-left"></i>';
    chatToggle.title = 'Ouvrir le chat';
}

// Envoyer un message
async function sendMessage() {
    const inputField = document.getElementById('chat-input-field');
    const message = inputField.value.trim();
    
    if (message === '') return;
    
    console.log('Envoi du message:', message);
    
    // Ajouter le message utilisateur
    addMessage('user', message);
    
    // Vider l'input
    inputField.value = '';
    
    // Désactiver le bouton d'envoi pendant le traitement
    const sendButton = document.querySelector('.send-button');
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Ajouter un indicateur "IA réfléchit..."
    addMessage('bot', '🤔 <em>L\'IA réfléchit à votre question...</em>');
    
    try {
        console.log('Appel de l\'API OpenAI...');
        
        // Appeler l'API OpenAI via Flask
        const response = await fetch('/api/chatbot/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });
        
        console.log('Réponse reçue:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Résultat:', result);
            
            if (result.success) {
                // Remplacer le message "IA réfléchit" par la vraie réponse
                replaceLastBotMessage(result.response);
            } else {
                replaceLastBotMessage(`Erreur: ${result.message}`);
            }
        } else {
            replaceLastBotMessage('Désolé, je ne peux pas traiter votre question pour le moment. Veuillez réessayer.');
        }
    } catch (error) {
        console.error('Erreur lors de l\'envoi du message:', error);
        replaceLastBotMessage('Désolé, une erreur est survenue. Veuillez réessayer.');
    } finally {
        // Réactiver le bouton d'envoi
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    }
}

// Envoyer une suggestion
function sendSuggestion(text) {
    console.log('Suggestion cliquée:', text);
    const inputField = document.getElementById('chat-input-field');
    inputField.value = text;
    sendMessage();
}

// Ajouter un message au chat
function addMessage(type, text) {
    const chatMessagesElement = document.getElementById('chat-messages');
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    
    // Vérifier que chatMessages est bien un tableau
    if (!Array.isArray(chatMessages)) {
        console.error('chatMessages n\'est pas un tableau:', chatMessages);
        chatMessages = [];
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.dataset.type = type;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = type === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.innerHTML = text; // Utiliser innerHTML pour supporter les balises HTML
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = timeString;
    
    content.appendChild(messageText);
    content.appendChild(messageTime);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessagesElement.appendChild(messageDiv);
    
    // Scroll vers le bas
    chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
    
    // Ajouter à l'historique
    try {
        chatMessages.push({
            type: type,
            text: text,
            time: timeString
        });
        console.log('Message ajouté à l\'historique, taille:', chatMessages.length);
    } catch (error) {
        console.error('Erreur lors de l\'ajout à l\'historique:', error);
    }
}

// Remplacer le dernier message du bot
function replaceLastBotMessage(newText) {
    const chatMessages = document.getElementById('chat-messages');
    const botMessages = chatMessages.querySelectorAll('.bot-message');
    
    if (botMessages.length > 0) {
        const lastBotMessage = botMessages[botMessages.length - 1];
        const messageText = lastBotMessage.querySelector('.message-text');
        if (messageText) {
            messageText.innerHTML = newText;
        }
    }
}

// Générer une réponse du bot
function generateBotResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    // Rechercher des mots-clés dans le message
    for (const [keyword, response] of Object.entries(chatBotResponses)) {
        if (lowerMessage.includes(keyword.toLowerCase())) {
            return response;
        }
    }
    
    // Réponses par défaut selon le contexte
    if (lowerMessage.includes('bonjour') || lowerMessage.includes('salut') || lowerMessage.includes('hello')) {
        return 'Bonjour ! Comment puis-je vous aider aujourd\'hui ?';
    }
    
    if (lowerMessage.includes('merci') || lowerMessage.includes('thanks')) {
        return 'De rien ! N\'hésitez pas si vous avez d\'autres questions.';
    }
    
    if (lowerMessage.includes('au revoir') || lowerMessage.includes('bye')) {
        return 'Au revoir ! Bonne journée !';
    }
    
    // Réponse par défaut
    return 'Je ne suis pas sûr de comprendre votre question. Pouvez-vous reformuler ou utiliser les suggestions ci-dessous ?';
}

// Gestion des touches dans l'input
function handleChatInputKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}



// Export des fonctions du chat
window.toggleChat = toggleChat;
window.closeChat = closeChat;
window.sendMessage = sendMessage;
window.sendSuggestion = sendSuggestion;