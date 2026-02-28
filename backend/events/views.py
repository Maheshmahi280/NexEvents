"""
============================================================================
Event Management API and Template Views
============================================================================
This module handles:
- User authentication (register, login, token management)
- Event management (create, read, update, delete)
- Event RSVP functionality
- Template rendering for HTML pages

Author: NexEvent Team
Version: 1.0.0
============================================================================
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .models import Event, UserProfile
from .serializers import EventSerializer
from .config import (
    ERROR_MESSAGES, SUCCESS_MESSAGES, VALIDATION_RULES,
    USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH, PASSWORD_MIN_LENGTH,
    EVENT_NAME_MIN_LENGTH, EVENT_NAME_MAX_LENGTH,
    EVENT_DESCRIPTION_MIN_LENGTH, EVENT_DESCRIPTION_MAX_LENGTH,
    EVENT_LOCATION_MIN_LENGTH, EVENT_LOCATION_MAX_LENGTH,
    EVENT_CATEGORIES
)

# Configure logger for debugging and monitoring
logger = logging.getLogger(__name__)


# ============================================================================
# TEMPLATE VIEWS - Serve HTML Pages
# ============================================================================
@require_http_methods(["GET"])
def index(request):
    """Serve home page - redirect logged-in users to their dashboard"""
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'Organizer':
                return redirect('organizer-dashboard')
            else:
                return redirect('seeker-dashboard')
        except Exception:
            pass
    return render(request, 'index.html')


@require_http_methods(["GET"])
def login_page(request):
    """Serve login page with optional role parameter"""
    # Redirect already authenticated users to their dashboard
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'Organizer':
                return redirect('organizer-dashboard')
            else:
                return redirect('seeker-dashboard')
        except Exception:
            pass
    role = request.GET.get('role', None)
    context = {'role': role}
    return render(request, 'login.html', context)


@require_http_methods(["GET"])
def register_page(request):
    """Serve registration page with optional role parameter"""
    # Redirect already authenticated users to their dashboard
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'Organizer':
                return redirect('organizer-dashboard')
            else:
                return redirect('seeker-dashboard')
        except Exception:
            pass
    role = request.GET.get('role', None)
    role_display = 'Organizer' if role == 'Organizer' else 'Attendee' if role == 'Seeker' else None
    context = {'role': role, 'role_display': role_display}
    return render(request, 'register.html', context)


@require_http_methods(["GET"])
def join_page(request):
    """Serve role selection page for new users"""
    # Redirect already authenticated users to their dashboard
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'Organizer':
                return redirect('organizer-dashboard')
            else:
                return redirect('seeker-dashboard')
        except Exception:
            pass
    return render(request, 'join.html')


@require_http_methods(["GET"])
def attending_join(request):
    """Serve attendee-specific registration page"""
    # Redirect already authenticated users to their dashboard
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'Organizer':
                return redirect('organizer-dashboard')
            else:
                return redirect('seeker-dashboard')
        except Exception:
            pass
    context = {'role': 'Seeker', 'role_display': 'Attendee'}
    return render(request, 'register.html', context)


@require_http_methods(["GET"])
def organizing_join(request):
    """Serve organizer-specific registration page"""
    # Redirect already authenticated users to their dashboard
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'Organizer':
                return redirect('organizer-dashboard')
            else:
                return redirect('seeker-dashboard')
        except Exception:
            pass
    context = {'role': 'Organizer', 'role_display': 'Organizer'}
    return render(request, 'register.html', context)


@require_http_methods(["GET"])
def dashboard_page(request):
    """Serve dashboard page - requires authentication"""
    from django.contrib.auth import login as auth_login
    
    # Check for JWT token in URL
    access_token = request.GET.get('token', None)
    if access_token and not request.user.is_authenticated:
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        from rest_framework.request import Request
        try:
            auth = JWTAuthentication()
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            drf_request = Request(request)
            auth_result = auth.authenticate(drf_request)
            if auth_result:
                request.user = auth_result[0]
                auth_login(request, auth_result[0], backend='django.contrib.auth.backends.ModelBackend')
        except AuthenticationFailed:
            return render(request, 'login.html')
    
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    
    return render(request, 'dashboard.html')


@require_http_methods(["GET"])
@ensure_csrf_cookie
def create_event_page(request):
    """Serve create event page - requires authentication"""
    from django.contrib.auth import login as auth_login
    
    # Check for JWT token in URL
    access_token = request.GET.get('token', None)
    if access_token and not request.user.is_authenticated:
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        from rest_framework.request import Request
        try:
            auth = JWTAuthentication()
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            drf_request = Request(request)
            auth_result = auth.authenticate(drf_request)
            if auth_result:
                request.user = auth_result[0]
                auth_login(request, auth_result[0], backend='django.contrib.auth.backends.ModelBackend')
        except AuthenticationFailed:
            return render(request, 'login.html')
    
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    
    return render(request, 'create-event.html')


@require_http_methods(["GET"])
def event_details_page(request, event_id):
    """Serve event details page"""
    return render(request, 'event-details.html', {'event_id': event_id})


@api_view(['POST'])
def register(request):
    """
    Register a new user account with role assignment.
    
    POST Parameters:
        - username (str): Unique username (3-150 chars)
        - email (str): Valid email address (max 254 chars)
        - password (str): Password (min 6 chars)
        - first_name (str): User's first name
        - last_name (str): User's last name
        - role (str): User role ('Seeker' or 'Organizer')
    
    Returns:
        - 201 Created: User registration successful with JWT tokens
        - 400 Bad Request: Validation errors or duplicate user
        - 500 Server Error: Unexpected error
    """
    try:
        # Extract and clean input data
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        role = request.data.get('role', 'Seeker').strip()

        # Validate all required fields
        errors = {}
        
        # Username validation
        if not username:
            errors['username'] = ERROR_MESSAGES['USERNAME_REQUIRED']
        elif len(username) < USERNAME_MIN_LENGTH:
            errors['username'] = ERROR_MESSAGES['USERNAME_TOO_SHORT']
        elif len(username) > USERNAME_MAX_LENGTH:
            errors['username'] = ERROR_MESSAGES['USERNAME_TOO_LONG']
        
        # Email validation
        if not email:
            errors['email'] = ERROR_MESSAGES['EMAIL_REQUIRED']
        elif '@' not in email or '.' not in email:
            errors['email'] = ERROR_MESSAGES['EMAIL_INVALID']
        elif len(email) > EMAIL_MAX_LENGTH:
            errors['email'] = ERROR_MESSAGES['EMAIL_TOO_LONG']
        
        # Password validation
        if not password:
            errors['password'] = ERROR_MESSAGES['PASSWORD_REQUIRED']
        elif len(password) < PASSWORD_MIN_LENGTH:
            errors['password'] = ERROR_MESSAGES['PASSWORD_TOO_SHORT']
        
        # Name validation
        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        
        # Role validation
        valid_roles = ['Seeker', 'Organizer']
        if role not in valid_roles:
            errors['role'] = f'Role must be one of: {", ".join(valid_roles)}'
        
        # Return validation errors if any
        if errors:
            logger.warning(f"Registration validation failed for {username}: {errors}")
            return Response(
                {'error': 'Validation failed', 'fields': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if username already exists (prevent duplicates)
        if User.objects.filter(username=username).exists():
            logger.info(f"Registration failed: Username '{username}' already taken")
            return Response(
                {'error': 'Validation failed', 'fields': {'username': ERROR_MESSAGES['USERNAME_TAKEN']}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email already exists (prevent duplicates)
        if User.objects.filter(email=email).exists():
            logger.info(f"Registration failed: Email '{email}' already registered")
            return Response(
                {'error': 'Validation failed', 'fields': {'email': ERROR_MESSAGES['EMAIL_TAKEN']}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new user with hashed password
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Explicitly create or update user profile with the selected role
        from events.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        logger.info(f"User profile created/updated for {username} with role: {role}")
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        logger.info(f"User registered successfully: {username} as {role}")
        
        return Response(
            {
                'message': SUCCESS_MESSAGES['REGISTRATION_SUCCESS'],
                'access': access_token,
                'refresh': refresh_token,
                'role': role,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        logger.error(f"Registration error: {type(e).__name__}: {str(e)}")
        return Response(
            {'error': ERROR_MESSAGES['REGISTRATION_FAILED'], 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def login(request):
    """
    Authenticate user credentials and return JWT tokens for session management.
    
    POST Parameters:
        - username (str): User's unique username (1-150 chars)
        - password (str): User's password (8+ chars)
    
    Returns:
        200 OK: {'message', 'access', 'refresh', 'user' object}
        400 Bad Request: {'error', 'fields'} - validation errors on required fields
        401 Unauthorized: {'error'} - incorrect username or password
        500 Internal Server Error: {'error', 'detail'} - unexpected server error
    """
    try:
        # Extract and sanitize input
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        logger.info(f"Login attempt for username: {username}")

        # Validate required fields using config constants
        errors = {}
        if not username:
            errors['username'] = ERROR_MESSAGES['USERNAME_REQUIRED']
            logger.warning("Login failed: missing username")
        
        if not password:
            errors['password'] = ERROR_MESSAGES['PASSWORD_REQUIRED']
            logger.warning("Login failed: missing password")
        
        # Return early if validation failed
        if errors:
            return Response(
                {'error': ERROR_MESSAGES['VALIDATION_FAILED'], 'fields': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user against database
        user = authenticate(username=username, password=password)

        # Check if authentication succeeded
        if user is None:
            logger.warning(f"Failed login attempt for username: {username}")
            return Response(
                {'error': ERROR_MESSAGES['INVALID_CREDENTIALS']},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens for authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Get user role
        role = 'Seeker'  # Default role
        if hasattr(user, 'profile'):
            role = user.profile.role
        
        logger.info(f"Successful login for user: {username} (ID: {user.id})")

        # Return tokens and user info
        return Response(
            {
                'message': SUCCESS_MESSAGES['LOGIN_SUCCESS'],
                'access': access_token,
                'refresh': refresh_token,
                'role': role,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Login error: {type(e).__name__}: {str(e)}")
        return Response(
            {'error': ERROR_MESSAGES['LOGIN_FAILED'], 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class EventListView(APIView):
    """
    GET /api/events/
    Retrieve all upcoming events with optional search and category filtering.
    
    Query Parameters:
        - search (str, optional): Search in name, description, location
        - category (str, optional): Filter by category (Tech, Arts, Sports, Education)
    
    Returns:
        200 OK: {'message', 'count', 'events' array, 'filters' applied}
        400 Bad Request: {'error', 'fields'} - invalid category provided
        500 Internal Server Error: {'error', 'detail'} - server error
    
    Access: Public (no authentication required)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Get all upcoming events ordered by date
            events = Event.objects.filter(
                date_time__gte=timezone.now()
            ).order_by('date_time')
            
            logger.info(f"EventListView accessed - Total events in db: {Event.objects.count()}")

            # Apply search filter if provided
            search_query = request.query_params.get('search', '').strip()
            if search_query:
                events = events.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(location__icontains=search_query)
                )
                logger.info(f"Search filter applied: '{search_query}' - Found {events.count()} events")

            # Apply category filter if provided
            category = request.query_params.get('category', '').strip()
            if category:
                # Validate category is in allowed choices
                if category not in dict(Event.CATEGORY_CHOICES):
                    logger.warning(f"Invalid category filter attempted: '{category}'")
                    return Response(
                        {
                            'error': ERROR_MESSAGES['VALIDATION_FAILED'],
                            'fields': {
                                'category': ERROR_MESSAGES['INVALID_CATEGORY']
                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                events = events.filter(category=category)
                logger.info(f"Category filter applied: '{category}' - Found {events.count()} events")

            # Serialize events
            serializer = EventSerializer(events, many=True)
            
            # Build user-friendly response message
            count = events.count()
            if count == 0:
                message = 'No events found matching your criteria'
            else:
                message = f'Found {count} event{"" if count == 1 else "s"}'

            return Response(
                {
                    'message': message,
                    'count': count,
                    'events': serializer.data,
                    'filters': {
                        'search': search_query or None,
                        'category': category or None,
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"EventListView error: {type(e).__name__}: {str(e)}")
            return Response(
                {
                    'error': ERROR_MESSAGES.get('EVENT_RETRIEVAL_FAILED', 'Failed to retrieve events'),
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventDetailView(APIView):
    """
    GET /api/events/<id>/
    Retrieve complete details for a specific event.
    
    URL Parameters:
        - event_id (int): Unique event identifier
    
    Returns:
        200 OK: {'event' object with all details}
        404 Not Found: {'error'} - event doesn't exist
        500 Internal Server Error: {'error', 'detail'} - server error
    
    Access: Public (no authentication required)
    """
    permission_classes = [AllowAny]

    def get(self, request, event_id):
        try:
            # Attempt to fetch event from database
            event = Event.objects.get(id=event_id)
            logger.info(f"EventDetailView accessed for event ID: {event_id} - '{event.name}'")
            
            # Serialize single event object
            serializer = EventSerializer(event)
            return Response(
                {'event': serializer.data},
                status=status.HTTP_200_OK
            )

        except Event.DoesNotExist:
            logger.warning(f"EventDetailView - Event not found with ID: {event_id}")
            return Response(
                {'error': ERROR_MESSAGES['EVENT_NOT_FOUND']},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"EventDetailView error: {type(e).__name__}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventCreateView(APIView):
    """
    POST /api/events/create/
    Create a new event with validation of all required fields.
    Only authenticated users can create events (organiser is set to current user).
    
    POST Parameters:
        - name (str, required): Event title (3-200 chars)
        - description (str, required): Event description (10-500 chars)
        - date_time (str, required): ISO format datetime (YYYY-MM-DDTHH:MM:SS)
        - location (str, required): Event location (2-200 chars)
        - category (str, required): One of Tech, Arts, Sports, Education
        - cover_image (str, optional): URL to cover image
    
    Returns:
        201 Created: {'message', 'event' object} - event successfully created
        400 Bad Request: {'error', 'fields'} - validation errors
        401 Unauthorized: {'error'} - not authenticated
        500 Internal Server Error: {'error', 'detail'} - server error
    
    Access: Authenticated users only
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"EventCreateView accessed - User: {request.user.username}")
            
            # Extract and sanitize input fields
            name = request.data.get('name', '').strip()
            description = request.data.get('description', '').strip()
            date_time = request.data.get('date_time', '')
            location = request.data.get('location', '').strip()
            category = request.data.get('category', '').strip()
            cover_image = request.data.get('cover_image', '').strip()
            ticket_price = request.data.get('ticket_price', 0)

            # Validate all required and optional fields using config constants
            errors = {}

            # Validate event name
            if not name:
                errors['name'] = ERROR_MESSAGES['NAME_REQUIRED']
            elif len(name) < VALIDATION_RULES['NAME_MIN_LENGTH']:
                errors['name'] = f'Event name must be at least {VALIDATION_RULES["NAME_MIN_LENGTH"]} characters'
            elif len(name) > VALIDATION_RULES['NAME_MAX_LENGTH']:
                errors['name'] = f'Event name must be at most {VALIDATION_RULES["NAME_MAX_LENGTH"]} characters'

            # Validate description
            if not description:
                errors['description'] = ERROR_MESSAGES['DESCRIPTION_REQUIRED']
            elif len(description) < VALIDATION_RULES['DESCRIPTION_MIN_LENGTH']:
                errors['description'] = f'Description must be at least {VALIDATION_RULES["DESCRIPTION_MIN_LENGTH"]} characters'
            elif len(description) > VALIDATION_RULES['DESCRIPTION_MAX_LENGTH']:
                excess_chars = len(description) - VALIDATION_RULES['DESCRIPTION_MAX_LENGTH']
                errors['description'] = f'Description is {len(description)} characters. Maximum is {VALIDATION_RULES["DESCRIPTION_MAX_LENGTH"]}. Please remove {excess_chars} characters.'

            # Validate date_time
            if not date_time:
                errors['date_time'] = ERROR_MESSAGES['DATE_TIME_REQUIRED']

            # Validate location
            if not location:
                errors['location'] = ERROR_MESSAGES['LOCATION_REQUIRED']
            elif len(location) < VALIDATION_RULES['LOCATION_MIN_LENGTH']:
                errors['location'] = f'Location must be at least {VALIDATION_RULES["LOCATION_MIN_LENGTH"]} characters'
            elif len(location) > VALIDATION_RULES['LOCATION_MAX_LENGTH']:
                errors['location'] = f'Location must be at most {VALIDATION_RULES["LOCATION_MAX_LENGTH"]} characters'

            # Validate category
            if not category:
                errors['category'] = ERROR_MESSAGES['CATEGORY_REQUIRED']
            elif category not in dict(Event.CATEGORY_CHOICES):
                errors['category'] = ERROR_MESSAGES['INVALID_CATEGORY']

            # Return early if validation failed
            if errors:
                logger.warning(f"Event creation validation failed - User: {request.user.username}")
                return Response(
                    {'error': ERROR_MESSAGES['VALIDATION_FAILED'], 'fields': errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Attempt to create event in database
            try:
                event = Event.objects.create(
                    name=name,
                    description=description,
                    date_time=date_time,
                    location=location,
                    category=category,
                    cover_image=cover_image if cover_image else None,
                    ticket_price=ticket_price,
                    organiser=request.user
                )
                logger.info(f"Event created successfully - ID: {event.id}, Name: '{name}', Organiser: {request.user.username}")
                
            except ValueError as ve:
                logger.warning(f"Event creation - Invalid date format - User: {request.user.username}")
                return Response(
                    {
                        'error': ERROR_MESSAGES['VALIDATION_FAILED'],
                        'fields': {'date_time': 'Invalid date format. Use format: YYYY-MM-DDTHH:MM:SS'}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Serialize and return created event
            serializer = EventSerializer(event)
            return Response(
                {
                    'message': SUCCESS_MESSAGES['EVENT_CREATED'],
                    'event': serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as ve:
            logger.warning(f"Event creation - ValueError: {str(ve)} - User: {request.user.username}")
            return Response(
                {
                    'error': ERROR_MESSAGES['VALIDATION_FAILED'],
                    'fields': {'date_time': 'Invalid date format. Use format: YYYY-MM-DDTHH:MM:SS'}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Event creation error: {type(e).__name__}: {str(e)} - User: {request.user.username}")
            return Response(
                {
                    'error': ERROR_MESSAGES['EVENT_CREATION_FAILED'],
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventDeleteView(APIView):
    """
    DELETE /api/events/<id>/delete/
    Delete an event and all associated relationships (interested_users, RSVPs).
    Only the event organiser can delete their own events.
    ManyToMany relationships are automatically cleaned up by Django ORM.
    
    URL Parameters:
        - event_id (int): Unique event identifier to delete
    
    Returns:
        200 OK: {'message', 'success', 'event_id', 'interested_users_removed'} - deletion successful
        403 Forbidden: {'error', 'success'} - user is not the organiser
        404 Not Found: {'error', 'success'} - event doesn't exist
        500 Internal Server Error: {'error', 'success', 'error_type'} - server error
    
    Access: Authenticated users only (must be event organiser)
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, event_id):
        try:
            # Fetch event from database
            event = Event.objects.get(id=event_id)
            logger.info(f"EventDeleteView accessed - Event ID: {event_id}, Event: '{event.name}', User: {request.user.username}")

            # Verify user is the event organiser
            if event.organiser != request.user:
                logger.warning(f"Delete attempt by non-organiser - Event ID: {event_id}, Attempted by: {request.user.username}, Organiser: {event.organiser.username}")
                return Response(
                    {'error': ERROR_MESSAGES['NOT_ORGANISER'], 'success': False},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get event details before deletion for logging and response
            event_name = event.name
            interested_count = event.interested_users.count()
            
            logger.info(f"Deleting event - ID: {event_id}, Name: '{event_name}', Interested users: {interested_count}")
            
            # Delete the event (Django ORM automatically handles ManyToMany cleanup)
            event.delete()
            
            logger.info(f"Event deleted successfully - ID: {event_id}, Name: '{event_name}'")
            
            return Response(
                {
                    'message': f'Event "{event_name}" deleted successfully',
                    'success': True,
                    'event_id': event_id,
                    'interested_users_removed': interested_count
                },
                status=status.HTTP_200_OK
            )

        except Event.DoesNotExist:
            logger.warning(f"Delete attempted on non-existent event - Event ID: {event_id}")
            return Response(
                {'error': ERROR_MESSAGES['EVENT_NOT_FOUND'], 'success': False},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as pe:
            logger.error(f"Permission error during deletion - Event ID: {event_id}, Error: {str(pe)}")
            return Response(
                {'error': f'Permission denied: {str(pe)}', 'success': False},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"EventDeleteView error: {type(e).__name__}: {str(e)}")
            return Response(
                {
                    'error': f'Error deleting event: {str(e)}',
                    'success': False,
                    'error_type': type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventRSVPView(APIView):
    """
    POST /api/events/<id>/rsvp/
    Toggle user interest in an event (add or remove from interested_users).
    This acts as both a subscribe and unsubscribe endpoint based on current status.
    Useful for implementing RSVP functionality with single endpoint.
    
    URL Parameters:
        - event_id (int): Unique event identifier to toggle interest
    
    Returns:
        200 OK: {'message', 'event' object} - user interest toggled successfully
        404 Not Found: {'error'} - event doesn't exist
        500 Internal Server Error: {'error'} - server error
    
    Access: Authenticated users only
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        try:
            # Fetch event from database
            event = Event.objects.get(id=event_id)
            logger.info(f"EventRSVPView accessed - Event ID: {event_id}, User: {request.user.username}")

            # Toggle user in interested_users (add if not present, remove if present)
            if request.user not in event.interested_users.all():
                # User is not interested yet, add them
                event.interested_users.add(request.user)
                message = SUCCESS_MESSAGES['RSVP_ADDED']
                logger.info(f"User added to interested list - Event ID: {event_id}, User: {request.user.username}")
            else:
                # User is already interested, remove them
                event.interested_users.remove(request.user)
                message = SUCCESS_MESSAGES['RSVP_REMOVED']
                logger.info(f"User removed from interested list - Event ID: {event_id}, User: {request.user.username}")

            # Serialize updated event
            serializer = EventSerializer(event)
            return Response(
                {
                    'message': message,
                    'event': serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Event.DoesNotExist:
            logger.warning(f"RSVP attempted on non-existent event - Event ID: {event_id}")
            return Response(
                {'error': ERROR_MESSAGES['EVENT_NOT_FOUND']},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"EventRSVPView error: {type(e).__name__}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserEventsView(APIView):
    """
    GET /api/events/my/
    Retrieve all events created by the authenticated user.
    Useful for user dashboard to show their created events.
    Events are sorted by most recently created first.
    
    Returns:
        200 OK: {'message', 'count', 'events' array, 'is_empty'} - list of user's events
        401 Unauthorized: {'error'} - not authenticated
        500 Internal Server Error: {'error', 'detail'} - server error
    
    Access: Authenticated users only
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logger.info(f"UserEventsView accessed - User: {request.user.username}")
            
            # Get all events created by current user, sorted by newest first
            events = Event.objects.filter(
                organiser=request.user
            ).order_by('-created_at')
            
            # Count total events for response message
            count = events.count()
            
            # Serialize events
            serializer = EventSerializer(events, many=True)
            
            # Build user-friendly response message
            if count == 0:
                message = 'You haven\'t created any events yet'
                logger.info(f"User has no events - User: {request.user.username}")
            else:
                message = f'You created {count} event{"" if count == 1 else "s"}'
                logger.info(f"Retrieved user events - User: {request.user.username}, Count: {count}")

            return Response(
                {
                    'message': message,
                    'count': count,
                    'events': serializer.data,
                    'is_empty': count == 0,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"UserEventsView error: {type(e).__name__}: {str(e)}")
            return Response(
                {
                    'error': ERROR_MESSAGES.get('EVENT_RETRIEVAL_FAILED', 'Failed to retrieve your events'),
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ============================================================================
# ROLE-BASED DASHBOARD VIEWS
# ============================================================================

@require_http_methods(["GET"])
def seeker_dashboard(request):
    """Serve attendee dashboard - restricted to Seeker role users"""
    from django.shortcuts import redirect
    from django.contrib.auth import login as auth_login
    import logging
    
    logger = logging.getLogger(__name__)
    
    # First check if user has access token in request (from script)
    access_token = request.GET.get('token', None)
    logger.info(f"Seeker dashboard accessed. Token provided: {bool(access_token)}, User authenticated: {request.user.is_authenticated}")
    
    if access_token:
        # If token is provided, verify it with JWT
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        from rest_framework.request import Request
        
        try:
            # Create a DRF Request object with the token
            auth = JWTAuthentication()
            # Manually set the token in the request for authentication
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            # Wrap Django request in DRF Request object for JWT auth
            drf_request = Request(request)
            auth_result = auth.authenticate(drf_request)
            if auth_result:
                request.user = auth_result[0]
                # Create Django session so subsequent page loads stay authenticated
                auth_login(request, auth_result[0], backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"JWT authentication successful for user: {request.user.username}")
            else:
                logger.warning("JWT authentication returned None")
        except AuthenticationFailed as e:
            logger.error(f"JWT authentication failed: {e}")
            return redirect('login-page')
    
    # Check if user is authenticated via session
    if not request.user.is_authenticated:
        return redirect('login-page')
    
    # Check if user has the correct role
    if hasattr(request.user, 'profile') and request.user.profile.role != 'Seeker':
        return redirect('organizer-dashboard')
    
    return render(request, 'seeker_dashboard.html')


@require_http_methods(["GET"])
def organizer_dashboard(request):
    """Serve organizer dashboard - restricted to Organizer role users"""
    from django.shortcuts import redirect
    from django.contrib.auth import login as auth_login
    import logging
    
    logger = logging.getLogger(__name__)
    
    # First check if user has access token in request (from script)
    access_token = request.GET.get('token', None)
    logger.info(f"Organizer dashboard accessed. Token provided: {bool(access_token)}, User authenticated: {request.user.is_authenticated}")
    
    if access_token:
        # If token is provided, verify it with JWT
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        from rest_framework.request import Request
        
        try:
            # Create a DRF Request object with the token
            auth = JWTAuthentication()
            # Manually set the token in the request for authentication
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            # Wrap Django request in DRF Request object for JWT auth
            drf_request = Request(request)
            auth_result = auth.authenticate(drf_request)
            if auth_result:
                request.user = auth_result[0]
                # Create Django session so subsequent page loads stay authenticated
                auth_login(request, auth_result[0], backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"JWT authentication successful for user: {request.user.username}")
            else:
                logger.warning("JWT authentication returned None")
        except AuthenticationFailed as e:
            logger.error(f"JWT authentication failed: {e}")
            return redirect('login-page')
    
    # Check if user is authenticated via session
    if not request.user.is_authenticated:
        return redirect('login-page')
    
    # Check if user has the correct role
    if hasattr(request.user, 'profile') and request.user.profile.role != 'Organizer':
        return redirect('seeker-dashboard')
    
    return render(request, 'organizer_dashboard.html')


@api_view(['POST'])
def logout_user(request):
    """
    Logout user (clear tokens on client side and Django session)
    
    Returns:
        200 OK: Logout successful
    """
    try:
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.info(f"User logged out: {username}")
        
        # Clear Django session
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)
        
        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Logout error: {type(e).__name__}: {str(e)}")
        return Response(
            {'error': 'Logout failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@require_http_methods(["GET"])
def user_profile(request):
    """
    Get current user's profile information including role
    
    Returns:
        200 OK: User profile data with role
        401 Unauthorized: User not authenticated
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'User not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user = request.user
        role = 'Seeker'  # Default role
        
        if hasattr(user, 'profile'):
            role = user.profile.role
        
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"User profile error: {type(e).__name__}: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve user profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )