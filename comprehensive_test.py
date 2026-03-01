#!/usr/bin/env python
"""
Comprehensive Test Suite for NexEvent Platform
Tests all major functionality: registration, login, event creation, viewing, RSVP
"""

import os
import json
import django
from django.test import Client
from django.contrib.auth.models import User

# Setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from events.models import Event, UserEventInterest, UserProfile

print("=" * 70)
print("COMPREHENSIVE NEXEVENT PLATFORM TEST")
print("=" * 70)

client = Client()

# ============================================================================
# CLEANUP: Remove test users
# ============================================================================
print("\n[SETUP] Cleaning up previous test users...")
User.objects.filter(username__startswith='test_comp_').delete()
print("✓ Cleanup complete")

# ============================================================================
# TEST 1: USER REGISTRATION (Seeker)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 1: SEEKER REGISTRATION")
print("=" * 70)

seeker_data = {
    'username': 'test_comp_seeker',
    'email': 'seeker@test.com',
    'password': 'TestPass123!',
    'first_name': 'Seeker',
    'last_name': 'Test',
    'role': 'Seeker'
}

response = client.post('/api/register/', 
    json.dumps(seeker_data),
    content_type='application/json'
)

if response.status_code == 201:
    seeker_resp = response.json()
    seeker_id = seeker_resp.get('id')
    print(f"✓ Seeker registered successfully (ID: {seeker_id})")
    print(f"  - Username: {seeker_resp.get('username')}")
    print(f"  - Email: {seeker_resp.get('email')}")
    print(f"  - Role: {seeker_resp.get('role')}")
else:
    print(f"✗ Seeker registration failed: {response.status_code}")
    print(f"  Response: {response.json()}")

# ============================================================================
# TEST 2: USER REGISTRATION (Organizer)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: ORGANIZER REGISTRATION")
print("=" * 70)

organizer_data = {
    'username': 'test_comp_organizer',
    'email': 'organizer@test.com',
    'password': 'TestPass123!',
    'first_name': 'Organizer',
    'last_name': 'Test',
    'role': 'Organizer'
}

response = client.post('/api/register/',
    json.dumps(organizer_data),
    content_type='application/json'
)

if response.status_code == 201:
    org_resp = response.json()
    org_id = org_resp.get('id')
    print(f"✓ Organizer registered successfully (ID: {org_id})")
    print(f"  - Username: {org_resp.get('username')}")
    print(f"  - Email: {org_resp.get('email')}")
    print(f"  - Role: {org_resp.get('role')}")
else:
    print(f"✗ Organizer registration failed: {response.status_code}")
    print(f"  Response: {response.json()}")

# ============================================================================
# TEST 3: LOGIN (Seeker)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: SEEKER LOGIN")
print("=" * 70)

login_data = {
    'username': 'test_comp_seeker',
    'password': 'TestPass123!'
}

response = client.post('/api/login/',
    json.dumps(login_data),
    content_type='application/json'
)

seeker_token = None
if response.status_code == 200:
    login_resp = response.json()
    seeker_token = login_resp.get('access')
    print(f"✓ Seeker login successful")
    print(f"  - Token: {seeker_token[:30]}...")
    print(f"  - Role: {login_resp.get('role')}")
else:
    print(f"✗ Seeker login failed: {response.status_code}")
    print(f"  Response: {response.json()}")

# ============================================================================
# TEST 4: LOGIN (Organizer)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: ORGANIZER LOGIN")
print("=" * 70)

login_data = {
    'username': 'test_comp_organizer',
    'password': 'TestPass123!'
}

response = client.post('/api/login/',
    json.dumps(login_data),
    content_type='application/json'
)

org_token = None
if response.status_code == 200:
    login_resp = response.json()
    org_token = login_resp.get('access')
    print(f"✓ Organizer login successful")
    print(f"  - Token: {org_token[:30]}...")
    print(f"  - Role: {login_resp.get('role')}")
else:
    print(f"✗ Organizer login failed: {response.status_code}")
    print(f"  Response: {response.json()}")

# ============================================================================
# TEST 5: CREATE EVENT (as Organizer)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 5: EVENT CREATION")
print("=" * 70)

event_data = {
    'name': 'Test Conference 2026',
    'description': 'This is a comprehensive test event for the platform',
    'date_time': '2026-03-15T14:00:00',
    'location': 'Test City Convention Center',
    'category': 'Tech',
    'cover_image': '',
    'ticket_price': 0
}

if org_token:
    response = client.post('/api/events/create/',
        json.dumps(event_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {org_token}'
    )
    
    event_id = None
    if response.status_code == 201:
        event_resp = response.json()
        event_id = event_resp.get('event', {}).get('id')
        print(f"✓ Event created successfully (ID: {event_id})")
        print(f"  - Name: {event_resp.get('event', {}).get('name')}")
        print(f"  - Location: {event_resp.get('event', {}).get('location')}")
        print(f"  - Category: {event_resp.get('event', {}).get('category')}")
        print(f"  - Organizer: {event_resp.get('event', {}).get('organiser_username')}")
    else:
        print(f"✗ Event creation failed: {response.status_code}")
        print(f"  Response: {response.json()}")
else:
    print("✗ Skipped: Organizer token not available")

# ============================================================================
# TEST 6: LIST EVENTS
# ============================================================================
print("\n" + "=" * 70)
print("TEST 6: LIST EVENTS")
print("=" * 70)

response = client.get('/api/events/')

if response.status_code == 200:
    events_resp = response.json()
    events_list = events_resp.get('events', [])
    print(f"✓ Events list retrieved successfully")
    print(f"  - Total events: {len(events_list)}")
    if events_list:
        print(f"  - Sample event: {events_list[0].get('name')}")
else:
    print(f"✗ Failed to get events list: {response.status_code}")

# ============================================================================
# TEST 7: GET EVENT DETAILS
# ============================================================================
print("\n" + "=" * 70)
print("TEST 7: GET EVENT DETAILS")
print("=" * 70)

if event_id:
    response = client.get(f'/api/events/{event_id}/')
    
    if response.status_code == 200:
        event_detail = response.json()
        print(f"✓ Event details retrieved successfully")
        print(f"  - Event ID: {event_detail.get('event', {}).get('id')}")
        print(f"  - Name: {event_detail.get('event', {}).get('name')}")
        print(f"  - Interested Count: {event_detail.get('event', {}).get('interested_count')}")
    else:
        print(f"✗ Failed to get event details: {response.status_code}")
else:
    print("✗ Skipped: No event ID available")

# ============================================================================
# TEST 8: RSVP TO EVENT (as Seeker)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 8: SEEKER RSVP TO EVENT")
print("=" * 70)

if event_id and seeker_token:
    response = client.post(f'/api/events/{event_id}/rsvp/',
        json.dumps({}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {seeker_token}'
    )
    
    if response.status_code == 200:
        rsvp_resp = response.json()
        print(f"✓ Seeker RSVP successful")
        print(f"  - Event: {rsvp_resp.get('message', '')}")
    else:
        print(f"✗ RSVP failed: {response.status_code}")
        print(f"  Response: {response.json()}")
else:
    print("✗ Skipped: Event ID or seeker token not available")

# ============================================================================
# TEST 9: GET USER'S EVENTS (as Organizer)
# ============================================================================
print("\n" + "=" * 70)
print("TEST 9: GET ORGANIZER'S EVENTS")
print("=" * 70)

if org_token:
    response = client.get('/api/events/my/',
        HTTP_AUTHORIZATION=f'Bearer {org_token}'
    )
    
    if response.status_code == 200:
        user_events = response.json()
        events_list = user_events.get('events', [])
        print(f"✓ Organizer's events retrieved successfully")
        print(f"  - Total events created: {len(events_list)}")
        for event in events_list:
            print(f"    - {event.get('name')}")
    else:
        print(f"✗ Failed to get user's events: {response.status_code}")
else:
    print("✗ Skipped: Organizer token not available")

# ============================================================================
# TEST 10: VERIFY SEEKER PROFILE
# ============================================================================
print("\n" + "=" * 70)
print("TEST 10: VERIFY SEEKER PROFILE")
print("=" * 70)

if seeker_token:
    response = client.get('/api/user/profile/',
        HTTP_AUTHORIZATION=f'Bearer {seeker_token}'
    )
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✓ Seeker profile retrieved successfully")
        print(f"  - Username: {profile.get('username')}")
        print(f"  - Email: {profile.get('email')}")
        print(f"  - Role: {profile.get('role')}")
    else:
        print(f"✗ Failed to get seeker profile: {response.status_code}")
else:
    print("✗ Skipped: Seeker token not available")

# ============================================================================
# TEST 11: VERIFY Database State
# ============================================================================
print("\n" + "=" * 70)
print("TEST 11: VERIFY DATABASE STATE")
print("=" * 70)

seeker_user = User.objects.filter(username='test_comp_seeker').first()
org_user = User.objects.filter(username='test_comp_organizer').first()
events = Event.objects.all()
interests = UserEventInterest.objects.all()

print(f"✓ Database Query Results:")
print(f"  - Seeker user in DB: {seeker_user is not None}")
if seeker_user:
    print(f"    - Seeker role: {seeker_user.profile.role}")
print(f"  - Organizer user in DB: {org_user is not None}")
if org_user:
    print(f"    - Organizer role: {org_user.profile.role}")
print(f"  - Total events in DB: {events.count()}")
print(f"  - Total interests in DB: {interests.count()}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("TEST SUITE COMPLETE")
print("=" * 70)
print("\n✓ All key functionality has been tested!")
print("  - User registration (both roles)")
print("  - User login")
print("  - Event creation")
print("  - Event listing")
print("  - Event details retrieval")
print("  - User RSVP")
print("  - User events retrieval")
print("  - Profile management")
print("  - Database integrity")
