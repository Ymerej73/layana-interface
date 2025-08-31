/* ==========================================
   LAYANA HOTEL - Professional Dashboard JS
   ========================================== */

// Global variables
let currentCalendarMonth = new Date().getMonth();
let currentCalendarYear = new Date().getFullYear();
let calendarData = {};
let isLoading = false;

// Cache DOM elements
const domCache = {
    systemStatus: null,
    calendarContainer: null,
    dayDetailsPanel: null,
    dashboardCards: null
};

// Animation utilities
const AnimationUtils = {
    fadeIn: (element, duration = 300) => {
        element.style.opacity = '0';
        element.style.display = 'block';
        element.animate([
            { opacity: 0, transform: 'translateY(10px)' },
            { opacity: 1, transform: 'translateY(0)' }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            fill: 'forwards'
        });
    },
    
    fadeOut: (element, duration = 300) => {
        element.animate([
            { opacity: 1, transform: 'translateY(0)' },
            { opacity: 0, transform: 'translateY(10px)' }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            fill: 'forwards'
        }).onfinish = () => element.style.display = 'none';
    },
    
    slideIn: (element, direction = 'left', duration = 400) => {
        const translateX = direction === 'left' ? '-100%' : '100%';
        element.animate([
            { opacity: 0, transform: `translateX(${translateX})` },
            { opacity: 1, transform: 'translateX(0)' }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            fill: 'forwards'
        });
    },
    
    scaleIn: (element, duration = 300) => {
        element.animate([
            { opacity: 0, transform: 'scale(0.9)' },
            { opacity: 1, transform: 'scale(1)' }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            fill: 'forwards'
        });
    },
    
    pulse: (element, duration = 600) => {
        element.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.05)' },
            { transform: 'scale(1)' }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        });
    }
};

// Loading states
const LoadingUtils = {
    showSkeleton: (container, count = 3) => {
        const skeletons = [];
        for (let i = 0; i < count; i++) {
            skeletons.push(`
                <div class="skeleton" style="height: 60px; margin-bottom: 10px; border-radius: 12px;"></div>
            `);
        }
        container.innerHTML = skeletons.join('');
    },
    
    showSpinner: (container) => {
        container.innerHTML = `
            <div class="loading-overlay">
                <div class="loading-spinner"></div>
            </div>
        `;
    },
    
    showContent: (container, content) => {
        container.innerHTML = content;
        AnimationUtils.fadeIn(container);
    }
};

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Layana Dashboard...');
    
    // Cache DOM elements
    domCache.systemStatus = document.getElementById('system-status');
    domCache.calendarContainer = document.getElementById('calendar-container');
    domCache.dayDetailsPanel = document.getElementById('day-details-panel');
    domCache.dashboardCards = document.querySelectorAll('.card');
    
    // Initialize components with staggered animations
    initializeWithAnimations();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize specific page components
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        initializeDashboard();
    }
    
    // Add hover effects to cards
    addCardHoverEffects();
    
    // Initialize tooltips
    initializeTooltips();
});

// ==========================================
// INITIALIZATION WITH ANIMATIONS
// ==========================================

function initializeWithAnimations() {
    // Stagger card animations
    domCache.dashboardCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s forwards`;
        }, 0);
    });
    
    // Animate navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach((link, index) => {
        link.style.animation = `slideInLeft 0.4s ease-out ${index * 0.05}s forwards`;
    });
}

// ==========================================
// DASHBOARD INITIALIZATION
// ==========================================

function initializeDashboard() {
    // Initialize system status with loading state
    if (domCache.systemStatus) {
        LoadingUtils.showSkeleton(domCache.systemStatus, 3);
        initializeSystemStatus();
    }
    
    // Initialize calendar with loading state
    if (domCache.calendarContainer) {
        LoadingUtils.showSpinner(domCache.calendarContainer);
        loadCalendarData();
    }
    
    // Initialize real-time updates
    setInterval(updateDashboardStats, 30000); // Update every 30 seconds
}

// ==========================================
// SYSTEM STATUS
// ==========================================

async function initializeSystemStatus() {
    await checkSystemStatus();
    // Update status every 30 seconds
    setInterval(checkSystemStatus, 30000);
}

async function checkSystemStatus() {
    try {
        const data = await fetchWithCache('/api/system/status', {
            cache: true,
            maxAge: 30 * 1000 // Cache for 30 seconds
        });
        
        updateSystemStatusUI(data);
    } catch (error) {
        console.error('❌ Error checking system status:', error);
        showSystemError();
    }
}

function updateSystemStatusUI(data) {
    if (!domCache.systemStatus) return;
    
    const statusHTML = `
        <div class="status-grid">
            ${createStatusIndicator('Serveur', data.server_status, data.server_message)}
            ${createStatusIndicator('Base de données', data.database_status, data.database_message)}
            ${createStatusIndicator('Données', data.data_status, data.data_message)}
        </div>
    `;
    
    LoadingUtils.showContent(domCache.systemStatus, statusHTML);
    
    // Add pulse animation to status dots
    setTimeout(() => {
        document.querySelectorAll('.status-dot').forEach(dot => {
            if (dot.classList.contains('status-online')) {
                dot.style.animation = 'pulse 2s infinite';
            }
        });
    }, 100);
}

function createStatusIndicator(label, status, message) {
    const statusClass = status === 'online' ? 'status-online' : 
                       status === 'warning' ? 'status-warning' : 'status-error';
    
    const statusIcon = status === 'online' ? '✓' : 
                      status === 'warning' ? '!' : '✗';
    
    return `
        <div class="status-indicator" data-tooltip="${message || 'Status: ' + status}">
            <div class="status-header">
                <span class="status-label">${label}</span>
                <span class="status-dot ${statusClass}">${statusIcon}</span>
            </div>
            <div class="status-message">${message || 'Opérationnel'}</div>
        </div>
    `;
}

function showSystemError() {
    if (!domCache.systemStatus) return;
    
    const errorHTML = `
        <div class="status-error-container">
            <p class="status-error-message">
                <span class="status-dot status-error">✗</span>
                Impossible de vérifier le statut du système
            </p>
        </div>
    `;
    
    domCache.systemStatus.innerHTML = errorHTML;
}

// ==========================================
// CALENDAR
// ==========================================

async function loadCalendarData() {
    if (isLoading) return;
    isLoading = true;
    
    try {
        const data = await fetchWithCache(
            `/api/calendar/${currentCalendarYear}/${currentCalendarMonth + 1}`,
            {
                cache: true,
                maxAge: 5 * 60 * 1000 // Cache for 5 minutes
            }
        );
        
        calendarData = data.calendar_data || {};
        
        // Show cache indicator if data is from cache
        if (data.fromCache) {
            showNotification('Données du calendrier chargées depuis le cache', 'info', 2000);
        }
        
        renderCalendar();
        
        // Prefetch adjacent months
        prefetchAdjacentMonths();
    } catch (error) {
        console.error('❌ Error loading calendar:', error);
        showCalendarError();
    } finally {
        isLoading = false;
    }
}

function prefetchAdjacentMonths() {
    // Prefetch previous month
    let prevMonth = currentCalendarMonth - 1;
    let prevYear = currentCalendarYear;
    if (prevMonth < 0) {
        prevMonth = 11;
        prevYear--;
    }
    
    // Prefetch next month
    let nextMonth = currentCalendarMonth + 1;
    let nextYear = currentCalendarYear;
    if (nextMonth > 11) {
        nextMonth = 0;
        nextYear++;
    }
    
    // Add to prefetch queue
    prefetchManager.add(`/api/calendar/${prevYear}/${prevMonth + 1}`);
    prefetchManager.add(`/api/calendar/${nextYear}/${nextMonth + 1}`);
}

function renderCalendar() {
    if (!domCache.calendarContainer) return;
    
    const calendarHTML = generateCalendarHTML();
    LoadingUtils.showContent(domCache.calendarContainer, calendarHTML);
    
    // Add click handlers to calendar days
    setTimeout(() => {
        document.querySelectorAll('.calendar-day[data-date]').forEach(day => {
            day.addEventListener('click', function() {
                const date = this.getAttribute('data-date');
                
                // Remove previous selection
                document.querySelectorAll('.calendar-day').forEach(d => 
                    d.classList.remove('selected')
                );
                
                // Add selection to clicked day
                this.classList.add('selected');
                AnimationUtils.pulse(this);
                
                // Show day details
                showDayDetails(date);
            });
        });
    }, 100);
}

function generateCalendarHTML() {
    const firstDay = new Date(currentCalendarYear, currentCalendarMonth, 1);
    const lastDay = new Date(currentCalendarYear, currentCalendarMonth + 1, 0);
    const prevLastDay = new Date(currentCalendarYear, currentCalendarMonth, 0);
    
    // Adjust for Monday start
    let startDate = firstDay.getDay();
    startDate = startDate === 0 ? 6 : startDate - 1;
    
    const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                       'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    const dayNames = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    
    let html = `
        <div class="calendar-header">
            <h3>${monthNames[currentCalendarMonth]} ${currentCalendarYear}</h3>
            <div class="calendar-nav">
                <button class="btn btn-icon" onclick="previousMonth()">
                    <span>←</span>
                </button>
                <button class="btn btn-icon" onclick="nextMonth()">
                    <span>→</span>
                </button>
            </div>
        </div>
        <div class="calendar-grid">
    `;
    
    // Day headers
    dayNames.forEach(day => {
        html += `<div class="calendar-day-header">${day}</div>`;
    });
    
    // Previous month days
    for (let i = startDate; i > 0; i--) {
        const day = prevLastDay.getDate() - i + 1;
        html += `<div class="calendar-day other-month">${day}</div>`;
    }
    
    // Current month days
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dateKey = `${currentCalendarYear}-${String(currentCalendarMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayData = calendarData[dateKey] || {};
        const hasActivity = dayData.arrivals?.length > 0 || dayData.departures?.length > 0;
        
        html += `
            <div class="calendar-day ${hasActivity ? 'has-activity' : ''}" 
                 data-date="${dateKey}">
                <div class="calendar-day-number">${day}</div>
                ${hasActivity ? `
                    <div class="calendar-day-indicators">
                        ${dayData.arrivals?.length > 0 ? 
                            `<span class="indicator arrival" data-tooltip="${dayData.arrivals.length} arrivée(s)">↓</span>` : ''}
                        ${dayData.departures?.length > 0 ? 
                            `<span class="indicator departure" data-tooltip="${dayData.departures.length} départ(s)">↑</span>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Next month days
    const remainingDays = 42 - (startDate + lastDay.getDate());
    for (let day = 1; day <= remainingDays; day++) {
        html += `<div class="calendar-day other-month">${day}</div>`;
    }
    
    html += '</div>';
    
    // Add legend
    html += `
        <div class="calendar-legend">
            <div class="legend-item">
                <span class="indicator arrival">↓</span>
                <span>Arrivées</span>
            </div>
            <div class="legend-item">
                <span class="indicator departure">↑</span>
                <span>Départs</span>
            </div>
        </div>
    `;
    
    return html;
}

function previousMonth() {
    currentCalendarMonth--;
    if (currentCalendarMonth < 0) {
        currentCalendarMonth = 11;
        currentCalendarYear--;
    }
    loadCalendarData();
}

function nextMonth() {
    currentCalendarMonth++;
    if (currentCalendarMonth > 11) {
        currentCalendarMonth = 0;
        currentCalendarYear++;
    }
    loadCalendarData();
}

function showCalendarError() {
    if (!domCache.calendarContainer) return;
    
    const errorHTML = `
        <div class="calendar-error">
            <p>Impossible de charger le calendrier</p>
            <button class="btn btn-primary" onclick="loadCalendarData()">
                Réessayer
            </button>
        </div>
    `;
    
    domCache.calendarContainer.innerHTML = errorHTML;
}

// ==========================================
// DAY DETAILS
// ==========================================

async function showDayDetails(date) {
    if (!domCache.dayDetailsPanel) return;
    
    // Show loading state
    domCache.dayDetailsPanel.style.display = 'block';
    LoadingUtils.showSpinner(domCache.dayDetailsPanel);
    AnimationUtils.slideIn(domCache.dayDetailsPanel, 'right');
    
    try {
        const dayData = calendarData[date] || { arrivals: [], departures: [] };
        
        const detailsHTML = `
            <div class="day-details-header">
                <h3>${formatDateFrench(date)}</h3>
                <button class="btn btn-icon" onclick="closeDayDetails()">
                    <span>×</span>
                </button>
            </div>
            <div class="day-details-content">
                ${generateActivitySection('Arrivées', dayData.arrivals, 'arrival')}
                ${generateActivitySection('Départs', dayData.departures, 'departure')}
            </div>
        `;
        
        setTimeout(() => {
            LoadingUtils.showContent(domCache.dayDetailsPanel, detailsHTML);
        }, 300);
        
    } catch (error) {
        console.error('❌ Error showing day details:', error);
        showDayDetailsError();
    }
}

function generateActivitySection(title, guests, type) {
    if (!guests || guests.length === 0) {
        return `
            <div class="activity-section">
                <h4 class="activity-title ${type}">${title}</h4>
                <p class="no-activity">Aucune ${title.toLowerCase()} prévue</p>
            </div>
        `;
    }
    
    const guestsList = guests.map((guest, index) => `
        <div class="guest-item" style="animation-delay: ${index * 0.05}s">
            <div class="guest-info">
                <span class="guest-name">${guest.guest_name || 'Client'}</span>
                <span class="guest-room">Chambre ${guest.room_number || '—'}</span>
            </div>
            ${guest.nights ? `<span class="guest-nights">${guest.nights} nuit(s)</span>` : ''}
        </div>
    `).join('');
    
    return `
        <div class="activity-section">
            <h4 class="activity-title ${type}">
                ${title} 
                <span class="activity-count">${guests.length}</span>
            </h4>
            <div class="guests-list">
                ${guestsList}
            </div>
        </div>
    `;
}

function closeDayDetails() {
    if (!domCache.dayDetailsPanel) return;
    
    AnimationUtils.fadeOut(domCache.dayDetailsPanel);
    
    // Remove selection from calendar
    document.querySelectorAll('.calendar-day').forEach(day => 
        day.classList.remove('selected')
    );
}

function showDayDetailsError() {
    if (!domCache.dayDetailsPanel) return;
    
    const errorHTML = `
        <div class="day-details-error">
            <p>Erreur lors du chargement des détails</p>
            <button class="btn btn-secondary" onclick="closeDayDetails()">
                Fermer
            </button>
        </div>
    `;
    
    domCache.dayDetailsPanel.innerHTML = errorHTML;
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function formatDateFrench(dateString) {
    const date = new Date(dateString + 'T12:00:00');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('fr-FR', options);
}

function updateDashboardStats() {
    // Animate stat updates
    document.querySelectorAll('.stat-value').forEach(stat => {
        AnimationUtils.pulse(stat);
    });
    
    // Re-check system status
    checkSystemStatus();
}

function addCardHoverEffects() {
    domCache.dashboardCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initializeTooltips() {
    // Initialize tooltips for elements with data-tooltip
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + rect.width / 2 + 'px';
            tooltip.style.top = rect.top - 10 + 'px';
            
            setTimeout(() => tooltip.classList.add('show'), 10);
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.classList.remove('show');
                setTimeout(() => {
                    this._tooltip.remove();
                    delete this._tooltip;
                }, 300);
            }
        });
    });
}

// ==========================================
// EVENT LISTENERS
// ==========================================

function setupEventListeners() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            // Refresh data when page becomes visible
            if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
                checkSystemStatus();
                loadCalendarData();
            }
        }
    });
    
    // Handle online/offline events
    window.addEventListener('online', function() {
        console.log('✅ Connection restored');
        showNotification('Connexion rétablie', 'success');
        updateDashboardStats();
    });
    
    window.addEventListener('offline', function() {
        console.log('❌ Connection lost');
        showNotification('Connexion perdue', 'error');
    });
}

// ==========================================
// NOTIFICATIONS
// ==========================================

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(notification);
    AnimationUtils.slideIn(notification, 'right', 300);
    
    setTimeout(() => {
        AnimationUtils.fadeOut(notification);
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ==========================================
// ROOM DETAILS (for current clients page)
// ==========================================

function viewRoomDetails(reservationId) {
    if (reservationId) {
        AnimationUtils.fadeOut(document.body);
        setTimeout(() => {
            window.location.href = `/reservation/${reservationId}`;
        }, 300);
    }
}

// ==========================================
// QUICK EDIT MODAL
// ==========================================

function openQuickEditModal(clientId, currentEmail, currentPhone) {
    const modal = document.getElementById('quick-edit-modal');
    if (!modal) return;
    
    document.getElementById('quick-edit-client-id').value = clientId;
    document.getElementById('quick-edit-email').value = currentEmail || '';
    document.getElementById('quick-edit-phone').value = currentPhone || '';
    
    modal.classList.add('show');
    AnimationUtils.scaleIn(modal.querySelector('.modal'));
}

function closeQuickEditModal() {
    const modal = document.getElementById('quick-edit-modal');
    if (!modal) return;
    
    AnimationUtils.fadeOut(modal.querySelector('.modal'));
    setTimeout(() => modal.classList.remove('show'), 300);
}

async function saveQuickEdit() {
    const clientId = document.getElementById('quick-edit-client-id').value;
    const email = document.getElementById('quick-edit-email').value;
    const phone = document.getElementById('quick-edit-phone').value;
    
    // Show loading state
    const saveButton = document.querySelector('.btn-primary[onclick="saveQuickEdit()"]');
    const originalText = saveButton.textContent;
    saveButton.textContent = 'Enregistrement...';
    saveButton.disabled = true;
    
    try {
        const response = await fetch(`/api/client/${clientId}/quick-edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Informations mises à jour avec succès', 'success');
            closeQuickEditModal();
            
            // Update the UI with new values
            const emailElement = document.querySelector(`[data-client-email="${clientId}"]`);
            const phoneElement = document.querySelector(`[data-client-phone="${clientId}"]`);
            
            if (emailElement) {
                emailElement.textContent = email || 'Non renseigné';
                AnimationUtils.pulse(emailElement);
            }
            if (phoneElement) {
                phoneElement.textContent = phone || 'Non renseigné';
                AnimationUtils.pulse(phoneElement);
            }
        } else {
            showNotification(data.error || 'Erreur lors de la mise à jour', 'error');
        }
    } catch (error) {
        console.error('❌ Error saving quick edit:', error);
        showNotification('Erreur de connexion', 'error');
    } finally {
        saveButton.textContent = originalText;
        saveButton.disabled = false;
    }
}

// ==========================================
// EXPORT FUNCTIONS
// ==========================================

// Make functions available globally
window.previousMonth = previousMonth;
window.nextMonth = nextMonth;
window.closeDayDetails = closeDayDetails;
window.viewRoomDetails = viewRoomDetails;
window.openQuickEditModal = openQuickEditModal;
window.closeQuickEditModal = closeQuickEditModal;
window.saveQuickEdit = saveQuickEdit;
window.loadCalendarData = loadCalendarData;

console.log('✨ Layana Dashboard Pro initialized successfully!');
