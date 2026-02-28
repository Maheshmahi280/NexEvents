/* ========================================
   Events Management Module
   ======================================== */

// Store all events for filtering
let allEvents = [];

/**
 * Initialize events page
 */
async function initializeEvents() {
    console.log('Initializing events page...');

    // Find event card container
    const container = document.getElementById('eventCardsContainer');
    if (!container) return;

    // Load initial events
    await loadEvents();

    // Set up search and filter event listeners
    setupEventListeners();

    // Update UI based on auth state
    updateAuthUI();
}

/**
 * Set up event listeners for search and filter
 */
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', handleCategoryFilter);
    }
}

/**
 * Debounce function to limit API calls
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Load events from API
 */
async function loadEvents() {
    try {
        console.log('[EVENTS] Loading events...');
        const container = document.getElementById('eventCardsContainer');

        if (!container) return;

        // Show loading state
        container.innerHTML = '<div class="loading">Loading events...</div>';

        // Fetch events from API
        const response = await apiGet('events/');
        allEvents = response.events || [];

        console.log(`[EVENTS] Loaded ${allEvents.length} events`);

        // Render events (passing empty search/category params)
        renderEvents(allEvents, '', '');

    } catch (error) {
        console.error('[EVENTS] Error:', error.message);
        const container = document.getElementById('eventCardsContainer');
        if (container) {
            container.innerHTML = `<div class="error-message">
                <p>Error loading events: ${error.message}</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">Please try refreshing the page</p>
            </div>`;
        }
    }
}

/**
 * Render events as cards
 * @param {Array} events - Array of event objects to render
 * @param {string} search - Search query (for empty state message)
 * @param {string} category - Category filter (for empty state message)
 */
function renderEvents(events, search = '', category = '') {
    const container = document.getElementById('eventCardsContainer');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Show appropriate empty state message
    if (events.length === 0) {
        let emptyMessage = '';

        if (search && category) {
            emptyMessage = `<div class="loading">
                <p style="margin-bottom: 1rem;">No events found for "${search}" in ${category}</p>
                <small style="color: var(--text-secondary);">Try different search terms or categories</small>
            </div>`;
        } else if (search) {
            emptyMessage = `<div class="loading">
                <p style="margin-bottom: 1rem;">No events found matching "${search}"</p>
                <small style="color: var(--text-secondary);">Try different keywords or browse all events</small>
            </div>`;
        } else if (category) {
            emptyMessage = `<div class="loading">
                <p style="margin-bottom: 1rem;">No ${category} events available right now</p>
                <small style="color: var(--text-secondary);">Check back later or explore other categories</small>
            </div>`;
        } else {
            emptyMessage = `<div class="loading">
                <p style="margin-bottom: 1rem;">No upcoming events at the moment</p>
                <small style="color: var(--text-secondary);">Be the first to create an event!</small>
            </div>`;
        }

        container.innerHTML = emptyMessage;
        return;
    }

    // Render each event
    events.forEach(event => {
        const card = createEventCard(event);
        if (card) container.appendChild(card);
    });
}

/**
 * Create event card element from template
 * @param {Object} event - Event object
 * @returns {Element} Event card element
 */
function createEventCard(event) {
    const template = document.getElementById('eventCardTemplate');
    if (!template) {
        console.error('Event card template not found');
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

    const categoryElement = card.querySelector('.category-text');
    if (categoryElement) categoryElement.textContent = event.category;

    const organiserElement = card.querySelector('.organiser-text');
    if (organiserElement) organiserElement.textContent = event.organiser_username || 'Unknown';

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

    const rsvpBtn = card.querySelector('.btn-rsvp');
    if (rsvpBtn) {
        rsvpBtn.textContent = 'Interested';
        rsvpBtn.onclick = () => handleEventRSVP(event.id, rsvpBtn);
    }

    return card;
}

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
 * Handle search input
 */
async function handleSearch() {
    const searchQuery = document.getElementById('searchInput') ? .value || '';
    const category = document.getElementById('categoryFilter') ? .value || '';

    await filterAndRenderEvents(searchQuery, category);
}

/**
 * Handle category filter change
 */
async function handleCategoryFilter() {
    const searchQuery = document.getElementById('searchInput') ? .value || '';
    const category = document.getElementById('categoryFilter') ? .value || '';

    await filterAndRenderEvents(searchQuery, category);
}

/**
 * Filter and render events
 * @param {string} search - Search query
 * @param {string} category - Category filter
 */
async function filterAndRenderEvents(search = '', category = '') {
    try {
        console.log(`[FILTER] Search="${search}", Category="${category}"`);

        const container = document.getElementById('eventCardsContainer');
        if (!container) return;

        // Show loading state
        container.innerHTML = '<div class="loading">Searching events...</div>';

        // Fetch filtered events from API
        try {
            const response = await apiGet(buildEventUrl(search, category));
            const filteredEvents = response.events || [];

            console.log(`[FILTER] Found ${filteredEvents.length} matching events`);

            // Render filtered events with context
            renderEvents(filteredEvents, search, category);
        } catch (apiError) {
            console.error('[FILTER] API call failed:', apiError);

            // Handle different error types
            if (apiError.message.includes('Invalid category')) {
                throw new Error('Invalid category selected. Please choose a valid category.');
            } else if (apiError.message.includes('Unauthorized') || apiError.message.includes('session')) {
                throw new Error('Your session has expired. Please login to continue.');
            }

            throw apiError;
        }

    } catch (error) {
        console.error('[FILTER] Error:', error.message);
        const container = document.getElementById('eventCardsContainer');
        if (container) {
            const errorMsg = error.message || 'Error filtering events. Please try again.';

            container.innerHTML = `<div class="error-message">
                <p>❌ ${errorMsg}</p>
                <small style="display: block; margin-top: 0.5rem;">Please try again or <a href="/" style="color: var(--primary);">refresh the page</a></small>
            </div>`;
        }
    }
}

/**
 * Build event API URL with query parameters
 * @param {string} search - Search query
 * @param {string} category - Category filter
 * @returns {string} API endpoint URL
 */
function buildEventUrl(search = '', category = '') {
    let url = 'events/';
    const params = new URLSearchParams();

    if (search) {
        params.append('search', search);
    }
    if (category) {
        params.append('category', category);
    }

    if (params.toString()) {
        url += `?${params.toString()}`;
    }

    return url;
}

/**
 * Handle event RSVP toggle
 * @param {number} eventId - Event ID
 * @param {Element} button - RSVP button element
 */
async function handleEventRSVP(eventId, button) {
    if (!isAuthenticated()) {
        alert('Please login to mark events as interested');
        window.location.href = '/login';
        return;
    }

    try {
        // Show loading state
        button.disabled = true;
        button.textContent = 'Loading...';

        // Toggle RSVP
        const response = await toggleEventRSVP(eventId);

        // Update button state
        button.textContent = response.message.includes('Added') ? '❤️ Interested' : 'Interested';
        button.disabled = false;

        console.log('RSVP toggled successfully');

    } catch (error) {
        console.error('Error toggling RSVP:', error);
        button.textContent = 'Interested';
        button.disabled = false;
        alert('Error updating interest. Please try again.');
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
 * Redirect to create event page
 */
function redirectToCreateEvent() {
    if (!isAuthenticated()) {
        alert('Please login to create events');
        window.location.href = '/login';
        return;
    }

    window.location.href = '/create-event';
}

/**
 * Update UI based on authentication state
 */
function updateAuthUI() {
    const isAuth = isAuthenticated();
    const authLinks = document.getElementById('auth-links');
    const dashboardLink = document.getElementById('dashboard-link');
    const logoutLink = document.getElementById('logout-link');
    const createEventBtn = document.getElementById('createEventBtn');

    if (authLinks) authLinks.style.display = isAuth ? 'none' : 'block';
    if (dashboardLink) dashboardLink.style.display = isAuth ? 'block' : 'none';
    if (logoutLink) logoutLink.style.display = isAuth ? 'block' : 'none';
    if (createEventBtn) createEventBtn.style.display = 'block';
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEvents);
} else {
    initializeEvents();
}