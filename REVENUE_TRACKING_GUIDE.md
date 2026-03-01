# Revenue Tracking Implementation Guide

## Overview
The revenue tracking and booking system has been successfully implemented for the HackRivals event management platform. This allows organizers to track actual revenue from event bookings and provides attendees with a complete booking experience.

## Features Implemented

### 1. Booking Model
- **Location**: `backend/events/models.py`
- **Fields**:
  - `event`: Foreign key to Event model
  - `attendee`: Foreign key to User model
  - `amount`: Decimal field storing ticket price at booking time
  - `status`: CharField with choices (confirmed, pending, cancelled)
  - `booking_date`: Auto-timestamp when booking is created
- **Constraints**: 
  - `unique_together(event, attendee)` - Prevents duplicate bookings

### 2. API Endpoints

#### Book an Event
- **Endpoint**: `POST /api/events/<event_id>/book/`
- **Authentication**: Required (JWT Bearer token)
- **Purpose**: Create a booking for an event
- **Response**:
  ```json
  {
    "message": "Booking confirmed!",
    "booking": {...},
    "revenue_to_organizer": 299.00
  }
  ```
- **Features**:
  - Captures event's ticket_price at booking time
  - Automatically adds event to user's bookmarks
  - Prevents duplicate bookings
  - Returns organizer revenue for user feedback

#### Get Organizer Revenue
- **Endpoint**: `GET /api/organizer/revenue/`
- **Authentication**: Required (JWT Bearer token)
- **Role Check**: Must be an Organizer
- **Purpose**: View revenue statistics across all organizer's events
- **Response**:
  ```json
  {
    "total_revenue": 1500.00,
    "total_bookings": 5,
    "events": [
      {
        "event_id": 1,
        "event_name": "Tech Conference 2024",
        "revenue": 900.00,
        "bookings": 3,
        "ticket_price": 300.00,
        "date_time": "2024-06-15T10:00:00Z",
        "location": "Convention Center"
      }
    ]
  }
  ```

#### Get User Bookings
- **Endpoint**: `GET /api/user/bookings/`
- **Authentication**: Required (JWT Bearer token)
- **Purpose**: View user's booking history
- **Response**:
  ```json
  {
    "bookings": [...],
    "count": 3
  }
  ```

### 3. Frontend Implementation

#### Seeker Dashboard (Attendee)
- **File**: `frontend/templates/seeker_dashboard.html`
- **Features**:
  - Booking confirmation dialog showing ticket price
  - Success message displaying revenue paid to organizer
  - Automatic bookmark addition on booking
  - Error handling for duplicate bookings
  - Real-time UI updates after booking

#### Organizer Dashboard
- **File**: `frontend/templates/organizer_dashboard.html`
- **Features**:
  - Total revenue card showing actual booking revenue
  - Automatically loads revenue data on page load
  - Displays revenue from confirmed bookings only
  - Handles authentication and token refresh

## Database Migration

The database has been successfully migrated with:
- `0002_booking.py` - Creates Booking model table
- `0005_merge...py` - Merges booking migration with existing migrations

**Migration Status**: ✅ Applied

## Revenue Calculation Logic

### For Bookings:
- When a user books an event, the current `event.ticket_price` is captured in `Booking.amount`
- This preserves historical pricing even if event ticket price changes later
- Status defaults to 'confirmed'

### For Organizer Revenue:
- Revenue is calculated as the sum of all `Booking.amount` where `status='confirmed'`
- Each event shows individual revenue and booking count
- Total revenue aggregates across all organizer's events

## How to Use

### For Attendees:
1. Browse events on the seeker dashboard
2. Click "Book Event" on any event card
3. Confirm the booking in the dialog
4. See confirmation with revenue amount going to organizer
5. View booking in "My Bookmarks" tab

### For Organizers:
1. Login and go to organizer dashboard
2. View "Total Revenue" card showing actual earnings
3. Access detailed revenue report via `/api/organizer/revenue/`
4. Track bookings per event in the API response

## Testing the Implementation

### Start the Server:
```powershell
cd d:\Hackrivals\backend
python manage.py runserver
```

### Test Booking Flow:
1. Login as a seeker/attendee
2. Navigate to seeker dashboard
3. Click "Book Event" on an event
4. Confirm booking and observe success message
5. Check that bookmarks tab now shows the event

### Test Revenue Display:
1. Login as an organizer
2. Navigate to organizer dashboard
3. Check "Total Revenue" card updates
4. Use browser dev tools to call `/api/organizer/revenue/` and view detailed breakdown

### API Testing with curl:
```bash
# Book an event
curl -X POST http://localhost:8000/api/events/1/book/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Get organizer revenue
curl -X GET http://localhost:8000/api/organizer/revenue/ \
  -H "Authorization: Bearer YOUR_ORGANIZER_TOKEN"

# Get user bookings
curl -X GET http://localhost:8000/api/user/bookings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Code Locations

### Backend Files:
- **Models**: `backend/events/models.py` - Booking model and Event helper methods
- **Serializers**: `backend/events/serializers.py` - BookingSerializer, EventSerializer enhancements
- **Views**: `backend/events/views.py` - BookEventView, OrganizerRevenueView, UserBookingsView
- **URLs**: `backend/events/urls.py` - API route definitions
- **Migrations**: `backend/events/migrations/0002_booking.py`, `0005_merge...py`

### Frontend Files:
- **Seeker Dashboard**: `frontend/templates/seeker_dashboard.html` - bookEvent() function
- **Organizer Dashboard**: `frontend/templates/organizer_dashboard.html` - loadOrganizerRevenue() function

## Security Considerations

1. **Authentication**: All endpoints require JWT authentication
2. **Authorization**: OrganizerRevenueView checks user role before allowing access
3. **Duplicate Prevention**: Database constraint prevents multiple bookings per user per event
4. **Token Refresh**: Frontend handles token expiration and automatic refresh

## Future Enhancements

Potential improvements:
1. Add payment gateway integration (Stripe, PayPal)
2. Implement booking cancellation with refund logic
3. Add booking history page for users
4. Create detailed revenue analytics dashboard for organizers
5. Add email notifications for booking confirmations
6. Implement booking status transitions (pending → confirmed)
7. Add export functionality for revenue reports (CSV, PDF)

## Support

For issues or questions about the revenue tracking system:
- Check Django logs for backend errors
- Use browser console to debug frontend API calls
- Verify JWT tokens are properly stored in localStorage
- Ensure migrations are applied: `python manage.py migrate`

---

**Implementation Date**: 2024
**Status**: ✅ Complete and Tested
**Database**: SQLite with Django ORM
**Backend**: Django 6.0.2 + DRF 3.16.1
**Authentication**: JWT (simplejwt)
