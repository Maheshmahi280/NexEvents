/* ========================================
   API Configuration and Helpers
   ======================================== */

// Base URL for all API requests
const BASE_URL = "/api/";

/**
 * Get authorization headers with JWT token
 * @returns {Object} Headers object with Authorization token
 */
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
}

/**
 * Generic API request helper with token refresh support
 * @param {string} endpoint - API endpoint (relative to BASE_URL)
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE, PATCH)
 * @param {Object} data - Request body data (for POST, PUT, DELETE)
 * @param {boolean} requiresAuth - Whether endpoint requires authentication
 * @param {boolean} isRetry - Internal flag to prevent infinite retry loops
 * @returns {Promise<Object>} Parsed response data
 */
async function apiRequest(endpoint, method = 'GET', data = null, requiresAuth = false, isRetry = false) {
    try {
        const url = `${BASE_URL}${endpoint}`;
        const headers = getAuthHeaders();

        // Check if authentication is required
        if (requiresAuth && !localStorage.getItem('access_token')) {
            throw new Error('Authentication required. Please login first.');
        }

        const options = {
            method: method,
            headers: headers,
        };

        // Add body for methods that support it
        if (method !== 'GET' && data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);

        // Handle response
        let responseData = {};
        try {
            responseData = await response.json();
        } catch (e) {
            // Response is not JSON (e.g., 404 HTML page)
            console.warn('[API] Response is not JSON');
            responseData = { error: `HTTP ${response.status}`, detail: 'Invalid response from server' };
        }

        // Handle 401 Unauthorized (token expired or invalid)
        if (response.status === 401) {
            if (requiresAuth && !isRetry) {
                console.warn('[TOKEN] Unauthorized (401) - Token may be expired');

                try {
                    // Try to refresh token
                    console.log('[TOKEN] Attempting token refresh...');
                    await refreshAccessToken();
                    console.log('[TOKEN] Token refreshed successfully - retrying request');

                    // Retry the original request with new token
                    return apiRequest(endpoint, method, data, requiresAuth, true);
                } catch (refreshError) {
                    console.error('[TOKEN] Refresh failed:', refreshError.message);
                    // Session invalid - redirect to login
                    clearTokens();
                    window.location.href = '/login?expired=true';
                    throw new Error('Your session has expired. Please login again.');
                }
            } else {
                // Not authenticated endpoint or retry failed
                throw new Error('Unauthorized - Please login again');
            }
        }

        // Handle 403 Forbidden (permission denied)
        if (response.status === 403) {
            const errorMessage = responseData.error || 'You do not have permission to perform this action';
            throw new Error(errorMessage);
        }

        // Handle 404 Not Found
        if (response.status === 404) {
            const errorMessage = responseData.error || 'The requested resource was not found';
            throw new Error(errorMessage);
        }

        // Handle 400 Bad Request (validation errors)
        if (response.status === 400) {
            let errorMessage = responseData.error || 'Invalid request';
            let details = '';

            // Include field-specific validation errors
            if (responseData.fields) {
                details = Object.entries(responseData.fields)
                    .map(([field, msg]) => `• ${field}: ${msg}`)
                    .join('\n');
            }

            const fullError = details ? `${errorMessage}\n${details}` : errorMessage;
            throw new Error(fullError);
        }

        // Handle 500 Internal Server Error
        if (response.status === 500) {
            console.error('[API] Server error:', responseData);
            throw new Error('Server error. Please try again later.');
        }

        // Handle other error responses
        if (!response.ok) {
            // Build error message with optional field details
            let errorMessage = responseData.error || responseData.detail || `Error: ${response.status}`;
            let details = '';

            // Include field-specific validation errors
            if (responseData.fields) {
                details = Object.entries(responseData.fields)
                    .map(([field, msg]) => `• ${field}: ${msg}`)
                    .join('\n');
            }

            const fullError = details ? `${errorMessage}\n${details}` : errorMessage;
            throw new Error(fullError);
        }

        return responseData;

    } catch (error) {
        console.error(`[API] ${method} ${endpoint} failed:`, error.message);
        throw error;
    }
}

/**
 * GET request helper
 * @param {string} endpoint - API endpoint
 * @param {boolean} requiresAuth - Whether endpoint requires authentication
 * @returns {Promise<Object>} Response data
 */
async function apiGet(endpoint, requiresAuth = false) {
    return apiRequest(endpoint, 'GET', null, requiresAuth);
}

/**
 * POST request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @param {boolean} requiresAuth - Whether endpoint requires authentication
 * @returns {Promise<Object>} Response data
 */
async function apiPost(endpoint, data = {}, requiresAuth = false) {
    return apiRequest(endpoint, 'POST', data, requiresAuth);
}

/**
 * DELETE request helper
 * @param {string} endpoint - API endpoint
 * @param {boolean} requiresAuth - Whether endpoint requires authentication
 * @returns {Promise<Object>} Response data
 */
async function apiDelete(endpoint, requiresAuth = false) {
    return apiRequest(endpoint, 'DELETE', null, requiresAuth);
}

/**
 * PUT request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @param {boolean} requiresAuth - Whether endpoint requires authentication
 * @returns {Promise<Object>} Response data
 */
async function apiPut(endpoint, data = {}, requiresAuth = false) {
    return apiRequest(endpoint, 'PUT', data, requiresAuth);
}

/**
 * PATCH request helper
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body data
 * @param {boolean} requiresAuth - Whether endpoint requires authentication
 * @returns {Promise<Object>} Response data
 */
async function apiPatch(endpoint, data = {}, requiresAuth = false) {
    return apiRequest(endpoint, 'PATCH', data, requiresAuth);
}

/* ========================================
   Token Management Helpers
   ======================================== */

/**
 * Store authentication tokens in localStorage
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - JWT refresh token
 */
function storeTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

/**
 * Get access token from localStorage
 * @returns {string|null} Access token or null
 */
function getAccessToken() {
    return localStorage.getItem('access_token');
}

/**
 * Get refresh token from localStorage
 * @returns {string|null} Refresh token or null
 */
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if access token exists
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Refresh access token using refresh token
 * @returns {Promise<Object>} Response with new access token
 */
async function refreshAccessToken() {
    try {
        const refreshToken = getRefreshToken();

        if (!refreshToken) {
            console.warn('[TOKEN] No refresh token available');
            throw new Error('No refresh token available. Please login again.');
        }

        const response = await fetch(`${BASE_URL}token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh: refreshToken,
            }),
        });

        if (response.status === 401) {
            console.warn('[TOKEN] Refresh token is invalid');
            clearTokens();
            throw new Error('Your session has expired. Please login again.');
        }

        if (response.status === 400) {
            console.warn('[TOKEN] Refresh token format is invalid');
            clearTokens();
            throw new Error('Your session has expired. Please login again.');
        }

        if (!response.ok) {
            console.error('[TOKEN] Token refresh failed with status:', response.status);
            clearTokens();
            throw new Error(`Token refresh failed (${response.status}). Please login again.`);
        }

        const data = await response.json();

        if (!data.access) {
            console.warn('[TOKEN] No access token in refresh response');
            clearTokens();
            throw new Error('Failed to refresh token. Please login again.');
        }

        // Store new access token
        localStorage.setItem('access_token', data.access);
        console.log('[TOKEN] Token refreshed and stored successfully');

        return data;

    } catch (error) {
        console.error('[TOKEN] Token refresh error:', error.message);
        clearTokens();
        throw error;
    }
}

/**
 * Clear all tokens and user data from localStorage
 */
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_data');
    console.log('All tokens cleared from localStorage');
}

/* ========================================
   Authentication Endpoints
   ======================================== */

/**
 * Register new user
 * @param {string} username - Username
 * @param {string} email - Email address
 * @param {string} password - Password
 * @returns {Promise<Object>} Response with user data
 */
async function registerUser(username, email, password, firstName = '', lastName = '', role = 'Seeker') {
    return apiPost('register/', {
        username: username,
        email: email,
        password: password,
        first_name: firstName,
        last_name: lastName,
        role: role,
    });
}

/**
 * Login user
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<Object>} Response with tokens and user data
 */
async function loginUser(username, password) {
    return apiPost('login/', {
        username: username,
        password: password,
    });
}

/**
 * Logout user (clears tokens)
 */
function logoutUser() {
    clearTokens();
}

/* ========================================
   Event Endpoints
   ======================================== */

/**
 * Get all upcoming events
 * @param {string} search - Optional search query
 * @param {string} category - Optional category filter
 * @returns {Promise<Object>} Response with events array
 */
async function getEvents(search = '', category = '') {
    let endpoint = 'events/';
    const params = new URLSearchParams();

    if (search) {
        params.append('search', search);
    }
    if (category) {
        params.append('category', category);
    }

    if (params.toString()) {
        endpoint += `?${params.toString()}`;
    }

    return apiGet(endpoint);
}

/**
 * Get event details
 * @param {number} eventId - Event ID
 * @returns {Promise<Object>} Response with event data
 */
async function getEventDetails(eventId) {
    return apiGet(`events/${eventId}/`);
}

/**
 * Create new event
 * @param {Object} eventData - Event data object
 * @returns {Promise<Object>} Response with created event data
 */
async function createEvent(eventData) {
    return apiPost('events/create/', eventData, true);
}

/**
 * Update event
 * @param {number} eventId - Event ID
 * @param {Object} eventData - Updated event data
 * @returns {Promise<Object>} Response with updated event data
 */
async function updateEvent(eventId, eventData) {
    return apiPut(`events/${eventId}/`, eventData, true);
}

/**
 * Delete event
 * @param {number} eventId - Event ID
 * @returns {Promise<Object>} Response
 */
async function deleteEvent(eventId) {
    return apiDelete(`events/${eventId}/delete/`, true);
}

/**
 * Get user's created events
 * @returns {Promise<Object>} Response with events array
 */
async function getUserEvents() {
    return apiGet('events/my/', true);
}

/**
 * Toggle RSVP for event (add/remove from interested)
 * @param {number} eventId - Event ID
 * @returns {Promise<Object>} Response with updated event data
 */
async function toggleEventRSVP(eventId) {
    return apiPost(`events/${eventId}/rsvp/`, {}, true);
}