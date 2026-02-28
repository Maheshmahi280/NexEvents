# Role-Based Authentication Quick Reference

## What Changed

✅ **COMPLETE**: Full role-based authentication system implemented and tested

## Key Features

### 1. Role Selection Page
- **URL**: `http://localhost:8000/join`
- **Behavior**: Users choose between "Attend Events" or "Organize Events"
- **Next Step**: Routes to role-specific registration

### 2. Role-Specific Registration
- **Attend Path**: `/join/attending` → Shows "Attendee" specific form
- **Organize Path**: `/join/organizing` → Shows "Organizer" specific form
- **Registration**: Form auto-fills role, user only fills other fields
- **Result**: User created with correct role, auto-logged in, redirected to correct dashboard

### 3. Dashboard Access Control
- **Seeker users** can only access `/seeker-dashboard`
  - Trying to access `/organizer-dashboard` → Redirect to `/seeker-dashboard`
- **Organizer users** can only access `/organizer-dashboard`
  - Trying to access `/seeker-dashboard` → Redirect to `/organizer-dashboard`

### 4. Login Flows
- **Generic Login**: `/login` shows standard form, redirects based on user's role
- **Quick Login**: `/login?role=Seeker` pre-selects login form role

## Testing the Implementation

### Test 1: Registration as Attendee
```
1. Visit http://localhost:8000/join
2. Click "Start Attending"
3. Fill registration form (role pre-selected as "Attendee")
4. Submit
5. Should auto-login and redirect to /seeker-dashboard
```

### Test 2: Registration as Organizer
```
1. Visit http://localhost:8000/join
2. Click "Start Organizing"
3. Fill registration form (role pre-selected as "Organizer")
4. Submit
5. Should auto-login and redirect to /organizer-dashboard
```

### Test 3: Dashboard Access Control
```
1. Login as Attendee
2. Try to visit /organizer-dashboard
3. Should redirect back to /seeker-dashboard
4. (Same in reverse for Organizer users)
```

## Code Locations

| Feature | File | Lines |
|---------|------|-------|
| Role selection page | templates/join.html | - |
| Registration form | templates/register.html | 284-311 |
| Attendee join endpoint | events/views.py | 78-81 |
| Organizer join endpoint | events/views.py | 84-87 |
| Seeker dashboard access | events/views.py | 821-843 |
| Organizer dashboard access | events/views.py | 846-873 |
| API routes | backend/urls.py | 35-36 |

## Database

- **Model**: UserProfile (`events/models.py`)
- **Role Field**: CharField with choices ['Seeker', 'Organizer']
- **Default**: 'Seeker' (auto-created when User is created)
- **How to Change**: User logged in, can change via API or admin panel (not yet implemented)

## API Response

```json
POST /api/login/
{
  "username": "john_doe"",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "Seeker" | "Organizer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

## Web Flow

```
USER VISITS SITE
       ↓
   HOMEPAGE (/)
       ↓
   CLICK "Join Now"
       ↓
   ROLE SELECTION (/join)
       ↓
   ┌─────────────────────────────────┐
   ↓                                 ↓
ATTEND (/join/attending)      ORGANIZE (/join/organizing)
   ↓                                 ↓
   └─────────────────────────────────┘
              ↓
       REGISTRATION FORM
       (role pre-selected)
              ↓
        CREATE ACCOUNT
              ↓
          AUTO LOGIN
              ↓
   ┌─────────────────────────────────┐
   ↓                                 ↓
/seeker-dashboard              /organizer-dashboard
(Attendee only)               (Organizer only)
   
   If wrong role tries to access
   the other dashboard:
        AUTOMATIC REDIRECT
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Unauthenticated access to dashboard | Redirect to `/login` |
| Wrong role accessing dashboard | Redirect to correct dashboard |
| Invalid JWT token | Request rejected by DRF |
| Missing Authorization header | Fall back to session auth |

## Security

- ✅ JWT tokens validated on every request
- ✅ User roles checked before rendering dashboard
- ✅ Automatic role-based redirects prevent unauthorized access
- ✅ No sensitive data in JWT (role stored in database)
- ✅ Token refresh supported

## Troubleshooting

### Problem: Registration page shows role selection when it shouldn't
**Solution**: Check that `/join/attending` or `/join/organizing` routes are mapped correctly in `backend/urls.py`

### Problem: Can access wrong dashboard
**Solution**: Verify JWT authentication is enabled and role validation is working in views.py (lines 821-873)

### Problem: Login redirects to wrong dashboard
**Solution**: Check that login endpoint returns correct role from UserProfile

## Future Enhancements

- [ ] Role switching UI (if user wants to change roles)
- [ ] Admin panel to manage user roles
- [ ] Email verification for signups
- [ ] Social login integration
- [ ] Remember me functionality
- [ ] Session expiration handling
