# ============================================================================
# Configuration Constants
# ============================================================================
# This file contains all configurable constants to avoid hardcoding values
# across the application. Update these values to customize the application.
# ============================================================================

# ============================================================================
# Application Configuration
# ============================================================================

APP_NAME = "NexEvent"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Discover and Manage Amazing Events"

# ============================================================================
# User Validation Rules
# ============================================================================

# Username validation
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 150

# Email validation
EMAIL_MAX_LENGTH = 254

# Password validation
PASSWORD_MIN_LENGTH = 6

# ============================================================================
# Event Validation Rules
# ============================================================================

# Event name validation
EVENT_NAME_MIN_LENGTH = 3
EVENT_NAME_MAX_LENGTH = 200

# Event description validation
EVENT_DESCRIPTION_MIN_LENGTH = 10
EVENT_DESCRIPTION_MAX_LENGTH = 500

# Event location validation
EVENT_LOCATION_MIN_LENGTH = 2
EVENT_LOCATION_MAX_LENGTH = 200

# Supported event categories
EVENT_CATEGORIES = {
    'Tech': 'Technology',
    'Arts': 'Arts & Culture',
    'Sports': 'Sports & Fitness',
    'Education': 'Education & Learning',
}

# ============================================================================
# Validation Rules Dictionary (for flexible access in code)
# ============================================================================

VALIDATION_RULES = {
    # User validation
    'USERNAME_MIN_LENGTH': USERNAME_MIN_LENGTH,
    'USERNAME_MAX_LENGTH': USERNAME_MAX_LENGTH,
    'EMAIL_MAX_LENGTH': EMAIL_MAX_LENGTH,
    'PASSWORD_MIN_LENGTH': PASSWORD_MIN_LENGTH,
    
    # Event validation
    'NAME_MIN_LENGTH': EVENT_NAME_MIN_LENGTH,
    'NAME_MAX_LENGTH': EVENT_NAME_MAX_LENGTH,
    'DESCRIPTION_MIN_LENGTH': EVENT_DESCRIPTION_MIN_LENGTH,
    'DESCRIPTION_MAX_LENGTH': EVENT_DESCRIPTION_MAX_LENGTH,
    'LOCATION_MIN_LENGTH': EVENT_LOCATION_MIN_LENGTH,
    'LOCATION_MAX_LENGTH': EVENT_LOCATION_MAX_LENGTH,
}

# ============================================================================
# Token Configuration
# ============================================================================

# Token refresh interval (in minutes)
TOKEN_REFRESH_INTERVAL = 30

# ============================================================================
# Frontend Configuration
# ============================================================================

# Debounce delay for search (in milliseconds)
SEARCH_DEBOUNCE_MS = 300

# Events per page in listings
EVENTS_PER_PAGE = 12

# ============================================================================
# Error Messages
# ============================================================================

ERROR_MESSAGES = {
    'USERNAME_REQUIRED': 'Username is required',
    'USERNAME_TOO_SHORT': f'Username must be at least {USERNAME_MIN_LENGTH} characters',
    'USERNAME_TOO_LONG': f'Username must be at most {USERNAME_MAX_LENGTH} characters',
    'USERNAME_TAKEN': 'This username is already taken',
    
    'EMAIL_REQUIRED': 'Email is required',
    'EMAIL_INVALID': 'Invalid email format',
    'EMAIL_TOO_LONG': 'Email is too long',
    'EMAIL_TAKEN': 'This email is already registered',
    
    'PASSWORD_REQUIRED': 'Password is required',
    'PASSWORD_TOO_SHORT': f'Password must be at least {PASSWORD_MIN_LENGTH} characters',
    'PASSWORD_MISMATCH': 'Passwords do not match',
    
    'EVENT_NAME_REQUIRED': 'Event name is required',
    'EVENT_NAME_TOO_SHORT': f'Event name must be at least {EVENT_NAME_MIN_LENGTH} characters',
    'EVENT_NAME_TOO_LONG': f'Event name must be at most {EVENT_NAME_MAX_LENGTH} characters',
    
    'DESCRIPTION_REQUIRED': 'Description is required',
    'DESCRIPTION_TOO_SHORT': f'Description must be at least {EVENT_DESCRIPTION_MIN_LENGTH} characters',
    'DESCRIPTION_TOO_LONG': f'Description must be at most {EVENT_DESCRIPTION_MAX_LENGTH} characters',
    
    'DATE_REQUIRED': 'Event date and time is required',
    'DATE_INVALID': 'Invalid date format. Use format: YYYY-MM-DDTHH:MM:SS',
    
    'LOCATION_REQUIRED': 'Location is required',
    'LOCATION_TOO_SHORT': f'Location must be at least {EVENT_LOCATION_MIN_LENGTH} characters',
    'LOCATION_TOO_LONG': f'Location must be at most {EVENT_LOCATION_MAX_LENGTH} characters',
    
    'NAME_REQUIRED': 'Event name is required',
    'NAME_TOO_SHORT': f'Event name must be at least 3 characters',
    'NAME_TOO_LONG': f'Event name must be at most 200 characters',
    
    'DATE_TIME_REQUIRED': 'Event date and time is required',
    'DATE_TIME_INVALID': 'Invalid date format. Use format: YYYY-MM-DDTHH:MM:SS',
    
    'CATEGORY_REQUIRED': 'Category is required',
    'CATEGORY_INVALID': 'Invalid category. Choose: Tech, Arts, Sports, or Education',
    
    'VALIDATION_FAILED': 'Validation failed',
    'INVALID_CREDENTIALS': 'Invalid username or password',
    'NOT_ORGANISER': 'You can only delete events you created',
    'EVENT_RETRIEVAL_FAILED': 'Failed to retrieve events',
    
    'SESSION_EXPIRED': 'Your session has expired. Please login again.',
    'UNAUTHORIZED': 'You are not authorized to perform this action.',
    'PERMISSION_DENIED': 'You can only delete events you created',
    'EVENT_NOT_FOUND': 'Event not found',
    'LOGIN_FAILED': 'Login failed',
    'REGISTRATION_FAILED': 'Registration failed',
    'EVENT_CREATION_FAILED': 'Event creation failed',
    'EVENT_DELETION_FAILED': 'Error deleting event',
}

# ============================================================================
# Success Messages
# ============================================================================

SUCCESS_MESSAGES = {
    'REGISTRATION_SUCCESS': 'User created successfully. Please login.',
    'LOGIN_SUCCESS': 'Login successful',
    'EVENT_CREATED': 'Event created successfully',
    'EVENT_DELETED': 'Event deleted successfully',
    'RSVP_ADDED': 'Added to interested events',
    'RSVP_REMOVED': 'Removed from interested events',
}

# ============================================================================
# API Endpoints (for reference)
# ============================================================================

API_ENDPOINTS = {
    'REGISTER': 'register/',
    'LOGIN': 'login/',
    'TOKEN_REFRESH': 'token/refresh/',
    'EVENTS_LIST': 'events/',
    'EVENTS_CREATE': 'events/create/',
    'EVENTS_MY': 'events/my/',
    'EVENT_DETAIL': 'events/{id}/',
    'EVENT_DELETE': 'events/{id}/delete/',
    'EVENT_RSVP': 'events/{id}/rsvp/',
}

# ============================================================================
# Page Routes (for reference)
# ============================================================================

PAGE_ROUTES = {
    'HOME': '/',
    'LOGIN': '/login',
    'REGISTER': '/register',
    'DASHBOARD': '/dashboard',
    'CREATE_EVENT': '/create-event',
    'EVENT_DETAIL': '/event/{id}',
}

# ============================================================================
# UI Configuration
# ============================================================================

# Color scheme (CSS variables)
UI_COLORS = {
    'PRIMARY': '#6366f1',
    'PRIMARY_DARK': '#4f46e5',
    'SUCCESS': '#10b981',
    'DANGER': '#ef4444',
    'WARNING': '#f59e0b',
    'SECONDARY': '#64748b',
}

# ============================================================================
# Cache Configuration (if needed in future)
# ============================================================================

CACHE_TIMEOUT_EVENTS = 300  # 5 minutes
CACHE_TIMEOUT_USERS = 600   # 10 minutes
