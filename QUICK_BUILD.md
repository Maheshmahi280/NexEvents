# Quick Build Commands

## Activation
```powershell
# PowerShell
d:\Hackrivals\venv\Scripts\Activate.ps1

# Command Prompt
d:\Hackrivals\venv\Scripts\activate.bat
```

## Development Server
```powershell
cd d:\Hackrivals\backend
python manage.py runserver
# Access at: http://127.0.0.1:8000
```

## Database
```powershell
# Check migrations status
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Testing
```powershell
cd d:\Hackrivals\backend
python test_deletion.py
```

## System Checks
```powershell
cd d:\Hackrivals\backend
python manage.py check
```

## Static Files
```powershell
# Collect static files (for production)
python manage.py collectstatic
```

## Django Admin
```powershell
# Access Django admin at:
# http://127.0.0.1:8000/admin
```

## API Endpoints
- Registration: `POST /api/register/`
- Login: `POST /api/login/`
- Events List: `GET /api/events/`
- Create Event: `POST /api/events/create/`
- Delete Event: `POST /api/events/<id>/delete/`
- RSVP Event: `POST /api/events/<id>/rsvp/`

## Environment Info
- Python: 3.13.7
- Django: 6.0.2
- Database: SQLite3 (db.sqlite3)
- Virtual Env: d:\Hackrivals\venv

## Status ✅
All dependencies installed, migrations applied, system checks passed.
Ready to build and deploy.
