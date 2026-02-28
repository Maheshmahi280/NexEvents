/* ========================================
   Dashboard Management Module
   ======================================== */

// Store user's events
let userEvents = [];
let interestedEvents = [];

/**
 * Format date to readable string
 * @param {Date} date - Date object
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Initialize dashboard page
 */
async function initializeDashboard() {
    console.log('Initializing dashboard...');

    // Check if user is authenticated
    if (!isAuthenticated()) {
        console.log('User not authenticated, redirecting to login');
        window.location.href = '/login';
        return;
    }

    // Load user data
    loadUserProfile();

    // Load user events
    await loadUserEvents();

    // Set up tab switching
    setupTabSwitching();
}

/**
 * Load and display user profile information
 */
function loadUserProfile() {
    try {
        const token = getAccessToken();
        if (!token) return;

        // Decode JWT token to get user info
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userId = payload.user_id;
        const username = payload.username || 'User';

        // Update UI with user info
        const userNameEl = document.getElementById('userName');
        const userEmailEl = document.getElementById('userEmail');
        const profileUsernameEl = document.getElementById('profileUsername');
        const memberSinceEl = document.getElementById('memberSince');

        if (userNameEl) userNameEl.textContent = username;
        if (userEmailEl) userEmailEl.textContent = `User ID: ${userId}`;
        if (profileUsernameEl) profileUsernameEl.value = username;
        if (memberSinceEl) memberSinceEl.value = new Date().toLocaleDateString();

        console.log(`Loaded user profile: ${username}`);

    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

/**
 * Set up dashboard tab switching
 */
function setupTabSwitching() {
    const menuItems = document.querySelectorAll('.menu-item');

    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Get target tab from href
            const href = item.getAttribute('href');
            const tabId = href.substring(1);

            // Remove active class from all items and tabs
            menuItems.forEach(m => m.classList.remove('active'));
            document.querySelectorAll('.dashboard-tab').forEach(tab => {
                tab.style.display = 'none';
            });

            // Add active class to clicked item
            item.classList.add('active');

            // Show selected tab
            const tab = document.getElementById(tabId);
            if (tab) {
                tab.style.display = 'block';

                // Load data if needed
                if (tabId === 'interested-events') {
                    loadInterestedEvents();
                }
            }
        });
    });
}

/**
 * Load user's created events
 */
async function loadUserEvents() {
    try {
        console.log('[LOAD] Loading user events...');

        const container = document.getElementById('myEventsContainer');
        if (!container) {
            console.error('[LOAD] myEventsContainer not found');
            return;
        }

        // Show loading state
        container.innerHTML = '<div class="loading">Loading your events...</div>';

        // Fetch user events from API
        let response;
        try {
            console.log('[LOAD] Calling getUserEvents API...');
            response = await getUserEvents();
            console.log('[LOAD] API response received:', response);
        } catch (apiError) {
            console.error('[LOAD] API call failed:', apiError);

            // Handle specific error cases
            if (apiError.message.includes('session has expired')) {
                throw new Error('Your session has expired. Please login again.');
            } else if (apiError.message.includes('Unauthorized')) {
                throw new Error('You are not authorized to access this. Please login again.');
            }

            throw new Error(`Failed to fetch events: ${apiError.message}`);
        }

        if (!response) {
            throw new Error('API returned no response');
        }

        userEvents = response.events || [];
        const isEmpty = response.is_empty === true;

        console.log(`[LOAD] Successfully loaded ${userEvents.length} user events`);

        // Render user events (with empty state support)
        renderUserEvents(userEvents, isEmpty);
        console.log('[LOAD] Events rendered successfully');

    } catch (error) {
        console.error('[LOAD] Complete error:', error);
        console.error('[LOAD] Error stack:', error.stack);
        const container = document.getElementById('myEventsContainer');
        if (container) {
            // Check if it's a session expiration error
            const isSessionError = error.message.includes('session has expired') ||
                error.message.includes('Unauthorized');

            if (isSessionError) {
                container.innerHTML = `<div class="error-message">
                    <p>❌ Your session has expired</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">Please <a href="/login" style="color: var(--primary);">login again</a> to continue.</p>
                </div>`;
            } else {
                container.innerHTML = `<div class="error-message">
                    <p>❌ Error loading your events</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">${error.message}</p>
                    <button onclick="location.reload()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: var(--danger); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem;">Retry</button>
                </div>`;
            }
        }
    }
}

/**
 * Render user's created events
 * @param {Array} events - Array of event objects
 * @param {boolean} isEmpty - Whether the dashboard is empty
 */
function renderUserEvents(events, isEmpty = false) {
    const container = document.getElementById('myEventsContainer');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Show "No events" message if empty
    if (events.length === 0 || isEmpty) {
        container.innerHTML = `<div class="empty-state">
            <p style="font-size: 1.1rem; margin-bottom: 1rem;">You haven't created any events yet</p>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Create your first event and start managing RSVPs from your dashboard!</p>
            <a href="/create-event" class="btn-primary" style="display: inline-block; padding: 0.75rem 1.5rem; text-decoration: none;">+ Create Event</a>
        </div>`;
        return;
    }

    // Render each event using dashboard template
    events.forEach(event => {
        const card = createDashboardEventCard(event);
        if (card) container.appendChild(card);
    });
}

/**
 * Create dashboard event card element from template
 * @param {Object} event - Event object
 * @returns {Element} Event card element
 */
function createDashboardEventCard(event) {
    const template = document.getElementById('dashboardEventTemplate');
    if (!template) {
        console.error('Dashboard event template not found');
        return null;
    }

    const card = template.content.cloneNode(true);

    // Format date
    const eventDate = new Date(event.date_time);
    const formattedDate = formatDate(eventDate);

    // Populate template
    const titleElement = card.querySelector('.event-title');
    if (titleElement) titleElement.textContent = event.name;

    const descElement = card.querySelector('.event-description');
    if (descElement) descElement.textContent = event.description;

    const dateElement = card.querySelector('.date-text');
    if (dateElement) dateElement.textContent = formattedDate;

    const locationElement = card.querySelector('.location-text');
    if (locationElement) locationElement.textContent = event.location;

    // Set image if available
    const imgElement = card.querySelector('.event-cover');
    if (imgElement && event.cover_image) {
        imgElement.src = event.cover_image;
        imgElement.alt = event.name;
    }

    // Set button actions
    const viewBtn = card.querySelector('.btn-view');
    if (viewBtn) {
        viewBtn.textContent = 'View Details';
        viewBtn.onclick = () => goToEventDetails(event.id);
    }

    const deleteBtn = card.querySelector('.btn-danger');
    if (deleteBtn) {
        deleteBtn.textContent = 'Delete';
        deleteBtn.onclick = () => {
            console.log(`[CARD] Delete button clicked for event ${event.id}`);
            handleDeleteEvent(event.id, card);
        };
    }

    return card;
}

/**
 * Handle event deletion
 * @param {number} eventId - Event ID
 * @param {Element} cardElement - Card element to remove
 */
async function handleDeleteEvent(eventId, cardElement) {
    // Confirm deletion
    if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
        return;
    }

    try {
        console.log(`[DELETE] Attempting to delete event ${eventId}...`);

        // Show loading state
        const deleteBtn = cardElement.querySelector('.delete-btn') || cardElement.querySelector('.btn-danger');
        if (deleteBtn) {
            deleteBtn.disabled = true;
            deleteBtn.textContent = 'Deleting...';
        }

        // Call API to delete event
        let response;
        try {
            response = await deleteEvent(eventId);
            console.log('[DELETE] API response:', response);
        } catch (apiError) {
            console.error('[DELETE] API call failed:', apiError);

            // Handle specific error scenarios
            if (apiError.message.includes('session has expired') || apiError.message.includes('Unauthorized')) {
                throw new Error('Your session has expired. Please login again.');
            } else if (apiError.message.includes('You can only delete')) {
                throw new Error('You can only delete events you created');
            } else if (apiError.message.includes('Event not found')) {
                throw new Error('This event no longer exists');
            } else if (apiError.message.includes('Permission denied')) {
                throw new Error('You do not have permission to delete this event');
            }

            throw new Error(`Delete failed: ${apiError.message || 'Unknown error'}`);
        }

        // Verify response indicates success
        if (response && (response.message || response.success !== false)) {
            console.log('[DELETE] Event deleted successfully');

            // Show success message
            alert('✅ Event deleted successfully!');

            // Reload user events
            console.log('[DELETE] Reloading user events...');
            await loadUserEvents();
            console.log('[DELETE] User events reloaded');
        } else {
            throw new Error('Delete returned unexpected response: ' + JSON.stringify(response));
        }

    } catch (error) {
        console.error('[DELETE] Complete error:', error);
        console.error('[DELETE] Error stack:', error.stack);

        // Restore button state
        const deleteBtn = cardElement.querySelector('.delete-btn') || cardElement.querySelector('.btn-danger');
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.textContent = 'Delete';
        }

        // Show detailed error message with appropriate icon
        const errorMessage = error.message || 'Unknown error occurred';

        // Determine if it's a session error
        if (errorMessage.includes('session has expired')) {
            alert('❌ Session Expired\n\n' + errorMessage + '\n\nRedirecting to login...');
            window.location.href = '/login';
        } else if (errorMessage.includes('Permission')) {
            alert('❌ Permission Denied\n\n' + errorMessage);
        } else if (errorMessage.includes('not found')) {
            alert('❌ Event Not Found\n\n' + errorMessage + '\n\nReloading events...');
            loadUserEvents();
        } else {
            alert(`❌ Error deleting event\n\n${errorMessage}\n\nPlease try again or contact support.`);
        }
    }
}

/**
 * Delete account
 */
async function deleteAccount() {
    // Confirm deletion
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone and will remove all your events.')) {
        return;
    }

    if (!confirm('This is your last warning. Deleting your account is permanent. Continue?')) {
        return;
    }

    try {
        console.log('Deleting account...');

        // Clear tokens
        clearTokens();

        // Redirect to home
        alert('Account deleted successfully. You have been logged out.');
        window.location.href = '/';

    } catch (error) {
        console.error('Error deleting account:', error);
        alert('Error deleting account. Please try again.');
    }
}

/**
 * Navigate to event details page
 * @param {number} eventId - Event ID
 */
function goToEventDetails(eventId) {
    window.location.href = `/event/${eventId}`;
}

/**
 * Navigate back to previous page
 */
function goBack() {
    window.history.back();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}