# NexEvents Project Structure

## Overview
Clear separation between Frontend and Backend for better organization and maintainability.

## Directory Layout

```
NexEvents/
├── frontend/                    # All frontend assets and templates
│   ├── static/                  # Static files (CSS, JS, Images)
│   │   ├── css/
│   │   │   └── style.css       # Main stylesheet
│   │   ├── js/
│   │   │   ├── api.js          # API utility functions
│   │   │   ├── auth.js         # Authentication helpers
│   │   │   ├── dashboard.js    # Dashboard functionality
│   │   │   └── events.js       # Event handling
│   │   └── style.css           # Additional styles
│   │
│   └── templates/               # Django HTML templates
│       ├── base.html           # Base template with navbar
│       ├── index.html          # Home page
│       ├── join.html           # Role selection page
│       ├── login.html          # Login page
│       ├── register.html       # Registration page
│       ├── seeker_dashboard.html    # Attendee dashboard
│       ├── organizer_dashboard.html # Organizer dashboard
│       ├── create-event.html   # Event creation page
│       └── event-details.html  # Event details page
│
├── backend/                     # Django backend application
│   ├── backend/                 # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py         # Django configuration (updated to use frontend folder)
│   │   ├── urls.py             # URL routing
│   │   ├── asgi.py             # ASGI config
│   │   └── wsgi.py             # WSGI config
│   │
│   ├── events/                  # Main Django app
│   │   ├── models.py           # Database models (User, Event, UserProfile)
│   │   ├── views.py            # View functions and API endpoints
│   │   ├── serializers.py      # DRF serializers
│   │   ├── urls.py             # App URL routing
│   │   ├── admin.py            # Django admin configuration
│   │   └── migrations/         # Database migrations
│   │
│   ├── manage.py               # Django management script
│   ├── db.sqlite3              # SQLite database
│   └── requirements.txt        # Python dependencies
│
├── README.md                    # Project documentation
├── PROJECT_STRUCTURE.md        # This file
└── .git/                        # Git repository
```

## Key Features

### Frontend (`/frontend`)
- **Static Files**: CSS, JavaScript, Images organized by type
- **Templates**: HTML templates with Django template tags
- All UI components centralized for easy management

### Backend (`/backend`)
- **Django Project**: `backend/` folder contains project settings
- **Events App**: `events/` app handles all business logic
- **Database**: SQLite for development
- **API**: RESTful API endpoints for frontend communication

## Technology Stack

### Frontend
- HTML5, CSS3, Bootstrap 5
- Vanilla JavaScript (no framework)
- Font Awesome icons

### Backend
- Django 6.0.2
- Django REST Framework 3.16.1
- SQLite3 (development)
- SimpleJWT for token authentication

## Running the Application

### Development Server
```bash
cd backend
python manage.py runserver
```

Access at: `http://127.0.0.1:8000`

### Static Files
Configure in `backend/backend/settings.py`:
- `STATIC_ROOT`: Compiled static files location
- `STATICFILES_DIRS`: Points to `frontend/static/`
- `STATIC_URL`: Web path for static files

### Templates
Django automatically finds templates in:
- `frontend/templates/` (main location)
- App-specific template directories

## API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - Login user
- `POST /api/logout/` - Logout user

### Events
- `GET /api/events/` - List all events
- `POST /api/events/create/` - Create event (auth required)
- `GET /api/events/<id>/` - Get event details
- `DELETE /api/events/<id>/delete/` - Delete event (auth required)
- `POST /api/events/<id>/rsvp/` - RSVP to event

### Dashboard Pages
- `GET /seeker-dashboard` - Attendee dashboard
- `GET /organizer-dashboard` - Organizer dashboard

## User Roles

1. **Seeker/Attendee** - Can browse and register for events
2. **Organizer** - Can create and manage events

## Notes
- Updated Django settings to reference `frontend/` folder for templates and static files
- Keep backend and frontend concerns separate
- All static assets should be placed in `frontend/static/`
- All templates should be placed in `frontend/templates/`
