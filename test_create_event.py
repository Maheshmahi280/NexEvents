#!/usr/bin/env python
"""
Test script to verify event creation API works
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from events.models import Event, UserProfile

# Clean up test user
test_username = 'test_organizer_create'
User.objects.filter(username=test_username).delete()

print("\n" + "="*60)
print("Testing Event Creation API")
print("="*60)

# Create test organizer
print("\n1. Creating test organizer user...")
user = User.objects.create_user(
    username=test_username,
    email=f'{test_username}@test.com',
    password='TestPass123!'
)
user.profile.role = 'Organizer'
user.profile.save()
print(f"   ✓ User created: {user.username}")
print(f"   ✓ User role: {user.profile.role}")

# Login to get token
print("\n2. Logging in to get token...")
client = Client()
login_response = client.post(
    '/api/login/',
    json.dumps({
        'username': test_username,
        'password': 'TestPass123!'
    }),
    content_type='application/json'
)

if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data.get('access')
    print(f"   ✓ Login successful")
    print(f"   ✓ Token: {token[:50]}...")
else:
    print(f"   ✗ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.json()}")
    sys.exit(1)

# Test event creation
print("\n3. Testing event creation API...")
tomorrow = datetime.now() + timedelta(days=1)
event_data = {
    'name': 'Test Event Creation',
    'description': 'This is a test event to verify the API works correctly',
    'date_time': tomorrow.strftime('%Y-%m-%dT10:00:00'),
    'location': 'Test Location',
    'category': 'Tech',
    'cover_image': '',
    'ticket_price': 0
}

print(f"   Event data: {json.dumps(event_data, indent=2)}")

create_response = client.post(
    '/api/events/create/',
    json.dumps(event_data),
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {token}'
)

print(f"\n   Status Code: {create_response.status_code}")
print(f"   Response: {json.dumps(create_response.json(), indent=2)}")

if create_response.status_code in [200, 201]:
    print("\n   ✓ Event creation successful!")
    response_data = create_response.json()
    
    # Verify event in database
    print("\n4. Verifying event in database...")
    event = Event.objects.filter(organizer=user).first()
    if event:
        print(f"   ✓ Event found in database")
        print(f"   ✓ Event ID: {event.id}")
        print(f"   ✓ Event name: {event.name}")
        print(f"   ✓ Event organizer: {event.organizer.username}")
        print(f"   ✓ Event date: {event.date_time}")
    else:
        print(f"   ✗ Event NOT found in database")
else:
    print(f"\n   ✗ Event creation failed!")
    if hasattr(create_response, 'json'):
        response_data = create_response.json()
        print(f"   Error response: {json.dumps(response_data, indent=2)}")

print("\n" + "="*60)
print("Test Complete")
print("="*60 + "\n")
