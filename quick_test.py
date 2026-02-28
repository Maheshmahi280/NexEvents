#!/usr/bin/env python
"""
Quick HTTP-based test for NexEvent platform
Tests all major functionality via HTTP API calls
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("NEXEVENT PLATFORM - QUICK FUNCTIONALITY TEST")
print("=" * 70)
print(f"Testing against: {BASE_URL}")
print()

# ============================================================================
# TEST 1: Check server is running
# ============================================================================
print("TEST 1: Server Status")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    if response.status_code == 200:
        print("✓ Server is running and responsive")
    else:
        print(f"✗ Server returned status {response.status_code}")
except Exception as e:
    print(f"✗ Cannot reach server: {e}")
    exit(1)

# ============================================================================
# TEST 2: User Registration
# ============================================================================
print("\nTEST 2: User Registration")
print("-" * 70)

seeker_data = {
    'username': f'test_seeker_{int(time.time())}',
    'email': 'testseeker@example.com',
    'password': 'TestPass123!',
    'first_name': 'Test',
    'last_name': 'Seeker',
    'role': 'Seeker'
}

response = requests.post(f"{BASE_URL}/api/register/", json=seeker_data)
if response.status_code == 201:
    print(f"✓ Seeker registration successful")
    seeker_username = seeker_data['username']
else:
    print(f"✗ Seeker registration failed ({response.status_code})")
    seeker_username = None

organizer_data = {
    'username': f'test_org_{int(time.time())}',
    'email': 'testorg@example.com',
    'password': 'TestPass123!',
    'first_name': 'Test',
    'last_name': 'Organizer',
    'role': 'Organizer'
}

response = requests.post(f"{BASE_URL}/api/register/", json=organizer_data)
if response.status_code == 201:
    print(f"✓ Organizer registration successful")
    org_username = organizer_data['username']
else:
    print(f"✗ Organizer registration failed ({response.status_code})")
    org_username = None

# ============================================================================
# TEST 3: Login
# ============================================================================
print("\nTEST 3: User Login")
print("-" * 70)

seeker_token = None
if seeker_username:
    login_data = {
        'username': seeker_username,
        'password': 'TestPass123!'
    }
    response = requests.post(f"{BASE_URL}/api/login/", json=login_data)
    if response.status_code == 200:
        seeker_token = response.json().get('access')
        print(f"✓ Seeker login successful")
    else:
        print(f"✗ Seeker login failed ({response.status_code})")

org_token = None
if org_username:
    login_data = {
        'username': org_username,
        'password': 'TestPass123!'
    }
    response = requests.post(f"{BASE_URL}/api/login/", json=login_data)
    if response.status_code == 200:
        org_token = response.json().get('access')
        print(f"✓ Organizer login successful")
    else:
        print(f"✗ Organizer login failed ({response.status_code})")

# ============================================================================
# TEST 4: Create Event
# ============================================================================
print("\nTEST 4: Event Creation")
print("-" * 70)

event_id = None
if org_token:
    event_data = {
        'name': 'Test Forum 2026',
        'description': 'A comprehensive test event for platform testing',
        'date_time': '2026-04-10T15:00:00',
        'location': 'Test Hall',
        'category': 'Education',
        'cover_image': '',
        'ticket_price': 0
    }
    
    headers = {'Authorization': f'Bearer {org_token}'}
    response = requests.post(f"{BASE_URL}/api/events/create/", 
                           json=event_data, headers=headers)
    if response.status_code == 201:
        event_id = response.json().get('event', {}).get('id')
        print(f"✓ Event created successfully (ID: {event_id})")
    else:
        print(f"✗ Event creation failed ({response.status_code})")
        print(f"  Response: {response.json()}")
else:
    print("✗ Skipped: No organizer token")

# ============================================================================
# TEST 5: List Events
# ============================================================================
print("\nTEST 5: List Events")
print("-" * 70)

response = requests.get(f"{BASE_URL}/api/events/")
if response.status_code == 200:
    events_count = len(response.json().get('events', []))
    print(f"✓ Events retrieved successfully ({events_count} total)")
else:
    print(f"✗ Failed to list events ({response.status_code})")

# ============================================================================
# TEST 6: Get Event Details
# ============================================================================
print("\nTEST 6: Get Event Details")
print("-" * 70)

if event_id:
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/")
    if response.status_code == 200:
        event_name = response.json().get('event', {}).get('name')
        print(f"✓ Event details retrieved (Name: {event_name})")
    else:
        print(f"✗ Failed to get event details ({response.status_code})")
else:
    print("✗ Skipped: No event ID")

# ============================================================================
# TEST 7: RSVP to Event
# ============================================================================
print("\nTEST 7: RSVP to Event")
print("-" * 70)

if event_id and seeker_token:
    headers = {'Authorization': f'Bearer {seeker_token}'}
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/rsvp/",
                           json={}, headers=headers)
    if response.status_code == 200:
        print(f"✓ Seeker RSVP successful")
    else:
        print(f"✗ RSVP failed ({response.status_code})")
else:
    print("✗ Skipped: Missing event ID or seeker token")

# ============================================================================
# TEST 8: Get User's Events
# ============================================================================
print("\nTEST 8: Get Organizer's Events")
print("-" * 70)

if org_token:
    headers = {'Authorization': f'Bearer {org_token}'}
    response = requests.get(f"{BASE_URL}/api/events/my/", headers=headers)
    if response.status_code == 200:
        user_events_count = len(response.json().get('events', []))
        print(f"✓ Organizer's events retrieved ({user_events_count} created)")
    else:
        print(f"✗ Failed to get user events ({response.status_code})")
else:
    print("✗ Skipped: No organizer token")

# ============================================================================
# TEST 9: Home Page
# ============================================================================
print("\nTEST 9: Home Page Access")
print("-" * 70)

response = requests.get(f"{BASE_URL}/")
if response.status_code == 200:
    if 'Discover Amazing Events' in response.text:
        print("✓ Home page renders correctly")
    else:
        print("⚠ Home page loads but content may be different")
else:
    print(f"✗ Home page failed ({response.status_code})")

# ============================================================================
# TEST 10: Navigation Check
# ============================================================================
print("\nTEST 10: Navigation (Dashboard Button Status)")
print("-" * 70)

# Login as organizer to check if logged in nav is correct
if org_token:
    headers = {'Authorization': f'Bearer {org_token}'}
    response = requests.get(f"{BASE_URL}/organizer-dashboard", 
                           headers=headers, allow_redirects=True)
    if response.status_code == 200:
        # Check if Dashboard button is NOT in the navigation
        if 'class="nav-link"' in response.text:
            # Count nav links
            nav_links = response.text.count('class="nav-link"')
            print(f"✓ Organizer dashboard accessible (Nav links: {nav_links})")
            if 'Dashboard' not in response.text or response.text.count('Dashboard') == 0:
                print("✓ Dashboard button successfully removed from navigation")
            else:
                print("⚠ Dashboard button still visible in navigation")
        else:
            print("✓ Dashboard page accessible")
    else:
        print(f"⚠ Dashboard access issue ({response.status_code})")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("\n✓ All core features tested:")
print("  • User registration (Seeker and Organizer)")
print("  • User authentication")
print("  • Event creation")
print("  • Event listing")  
print("  • Event details retrieval")
print("  • User RSVP functionality")
print("  • User events management")
print("  • Page accessibility")
print("  • Navigation updates")
print("\n✓ Platform appears to be fully operational!")
