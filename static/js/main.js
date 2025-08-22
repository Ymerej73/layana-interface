// Main JavaScript file for Layana Hotel Management System

// Variables globales
let currentClientId = null;
let currentQuickEditField = null;
let currentTheme = localStorage.getItem('theme') || 'light';
let searchTimeout = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    loadSettings();
    initializeEventListeners();
    initializeSearchDebouncing();
    initializeCalendar();
    initializeSystemStatus();
});

// Initialisation des écouteurs d'événements
function initializeEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
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



// Gestion du thème
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.classList.toggle('dark-theme', currentTheme === 'dark');
    localStorage.setItem('theme', currentTheme);
    
    // Mettre à jour l'icône du bouton
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

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

function previousMonth() {
    currentCalendarMonth--;
    if (currentCalendarMonth < 1) {
        currentCalendarMonth = 12;
        currentCalendarYear--;
    }
    loadCalendarData();
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
window.toggleTheme = toggleTheme;
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



// Initialisation du statut système
function initializeSystemStatus() {
    checkSystemStatus();
    // Vérifier le statut toutes les 30 secondes
    setInterval(checkSystemStatus, 30000);
}

// Vérification du statut système
async function checkSystemStatus() {
    try {
        console.log('Vérification du statut système...');
        const response = await fetch('/api/system/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Données de statut reçues:', data);
        
        updateStatusIndicator('supabase-status', data.supabase.status, data.supabase.response_time);
        updateStatusIndicator('database-status', data.database.status, data.database.response_time);
        updateStatusIndicator('api-status', data.api.status, data.api.response_time);
        
        // Mettre à jour les métriques
        const responseTimeElement = document.getElementById('response-time');
        const lastCheckElement = document.getElementById('last-check');
        
        if (responseTimeElement) {
            const times = [data.supabase.response_time, data.database.response_time, data.api.response_time].filter(t => t !== null);
            if (times.length > 0) {
                const avgResponseTime = Math.round(times.reduce((a, b) => a + b, 0) / times.length);
                responseTimeElement.textContent = `${avgResponseTime}ms`;
            } else {
                responseTimeElement.textContent = 'N/A';
            }
        }
        
        if (lastCheckElement) {
            const now = new Date();
            lastCheckElement.textContent = now.toLocaleTimeString();
        }
    } catch (error) {
        console.error('Erreur lors de la vérification du statut:', error);
        updateStatusIndicator('supabase-status', 'offline');
        updateStatusIndicator('database-status', 'offline');
        updateStatusIndicator('api-status', 'offline');
        
        // Mettre à jour les métriques en cas d'erreur
        const responseTimeElement = document.getElementById('response-time');
        const lastCheckElement = document.getElementById('last-check');
        
        if (responseTimeElement) {
            responseTimeElement.textContent = 'Erreur';
        }
        
        if (lastCheckElement) {
            const now = new Date();
            lastCheckElement.textContent = now.toLocaleTimeString();
        }
    }
}

// Mise à jour des indicateurs de statut
function updateStatusIndicator(elementId, status, responseTime = null) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const dot = element.querySelector('.status-dot');
    const text = element.querySelector('span');
    
    if (!dot || !text) return;
    
    // Supprimer toutes les classes de statut
    dot.classList.remove('status-online', 'status-offline', 'status-checking', 'status-warning');
    
    // Ajouter la classe appropriée
    dot.classList.add(`status-${status}`);
    
    // Mettre à jour le texte selon l'élément
    let statusText = '';
    switch (elementId) {
        case 'supabase-status':
            statusText = status === 'online' ? 
                (responseTime ? `Supabase connecté (${responseTime}ms)` : 'Supabase connecté') :
                'Supabase déconnecté';
            break;
        case 'database-status':
            statusText = status === 'online' ? 
                (responseTime ? `Base de données connectée (${responseTime}ms)` : 'Base de données connectée') :
                'Base de données déconnectée';
            break;
        case 'api-status':
            statusText = status === 'online' ? 
                (responseTime ? `API opérationnelle (${responseTime}ms)` : 'API opérationnelle') :
                'API non disponible';
            break;
        default:
            statusText = status === 'online' ? 'Connecté' : 'Déconnecté';
    }
    
    text.textContent = statusText;
}

// Rafraîchir le statut système
function refreshSystemStatus() {
    const button = event.target.closest('button');
    if (button) {
        const icon = button.querySelector('i');
        icon.classList.add('fa-spin');
        
        checkSystemStatus().finally(() => {
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        });
    }
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
window.refreshSystemStatus = refreshSystemStatus;
window.previousMonth = previousMonth;
window.nextMonth = nextMonth;
window.showDayDetails = showDayDetails;
window.closeDayDetails = closeDayDetails;