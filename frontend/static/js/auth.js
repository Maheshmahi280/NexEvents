/* ========================================
   Authentication Module - NexEvent
   ======================================== */

/**
 * Clear all error messages in a form
 * @param {Element} form - Form element
 */
function clearFormErrors(form) {
    var errorElements = form.querySelectorAll('.error-message');
    errorElements.forEach(function(error) {
        error.textContent = '';
        error.style.display = 'none';
    });
}

/**
 * Display error message
 * @param {string} message - Error message
 * @param {Element} element - Element to display error in
 */
function displayError(message, element) {
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
    }
}

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} True if valid email
 */
function isValidEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Confirm logout with warning modal
 */
function confirmLogout(event) {
    if (event) {
        event.preventDefault();
    }

    // Show the logout warning modal using Bootstrap
    const logoutModal = document.getElementById('logoutWarningModal');
    if (logoutModal) {
        // Use Bootstrap 5 to show the modal
        const modal = new bootstrap.Modal(logoutModal);
        modal.show();
    } else {
        // Fallback if modal doesn't exist
        if (confirm('Are you sure you want to logout?\n\nYou will need to login again to access your account.')) {
            logout();
        }
    }
}

/**
 * Logout user
 */
function logout() {
    try {
        console.log('Logging out...');

        // Clear all stored data
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_data');
        sessionStorage.clear();
        console.log('All tokens and session cleared');

        // Call backend logout endpoint
        fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        }).then(function(response) {
            console.log('Backend logout response:', response.status);
        }).catch(function(error) {
            console.error('Backend logout error:', error);
        }).finally(function() {
            console.log('Redirecting to home page...');
            window.location.href = '/';
        });

    } catch (error) {
        console.error('Logout error:', error);
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = '/';
    }
}

/**
 * Get CSRF token from cookie
 */
function getCSRFToken() {
    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

console.log('[AUTH] Auth module loaded successfully');