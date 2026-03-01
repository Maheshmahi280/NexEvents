#!/usr/bin/env python
"""
Complete End-to-End Test of Event Creation API
Tests the full flow: login -> token generation -> event creation
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from events.models import Event

print("\n" + "="*70)
print("END-TO-END EVENT CREATION TEST")
print("="*70)

# Initialize test client
client = Client()

# Create test user
print("\n[1] Creating/getting test user...")
test_user, created = User.objects.get_or_create(
    username='e2etest',
    defaults={
        'email': 'e2etest@example.com',
        'first_name': 'E2E',
        'last_name': 'Test',
    }
)
if created:
    test_user.set_password('e2etest123')
    test_user.save()
    print(f"    [OK] Created user: {test_user.username}")
else:
    test_user.set_password('e2etest123')
    test_user.save()
    print(f"    [OK] Using existing user: {test_user.username}")

# Step 1: Login and get tokens
print("\n[2] Testing login endpoint...")
login_data = {
    'username': 'e2etest',
    'password': 'e2etest123'
}
response = client.post('/api/login/', login_data, content_type='application/json')
print(f"    Status: {response.status_code}")

if response.status_code == 200:
    login_response = json.loads(response.content)
    access_token = login_response.get('access')
    print(f"    [OK] Login successful")
    print(f"    [OK] Access token received (length: {len(access_token)})")
else:
    print(f"    [ERROR] Login failed: {response.content}")
    sys.exit(1)

# Step 2: Test event creation with JWT token
print("\n[3] Testing event creation with JWT token...")

event_data = {
    'name': 'E2E Test Event',
    'description': 'This is a test event created by the E2E test script',
    'date_time': (timezone.now() + timedelta(days=1)).isoformat(),
    'location': 'Test Location',
    'category': 'Tech',
    'cover_image': '',
    'ticket_price': 0
}

# Add JWT Bearer token to request
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

response = client.post(
    '/api/events/create/',
    json.dumps(event_data),
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {access_token}'
)

print(f"    Status: {response.status_code}")
response_data = json.loads(response.content)

if response.status_code == 201:
    print(f"    [OK] Event created successfully!")
    event_data_response = response_data.get('event', {})
    print(f"    Event ID: {event_data_response.get('id')}")
    print(f"    Event name: {event_data_response.get('name')}")
    print("\n    TEST PASSED: Event creation works with JWT auth!")
else:
    print(f"    [ERROR] Event creation failed!")
    print(f"    Response: {response_data}")
    if response.status_code == 401:
        print(f"    [ANALYSIS] 401 Unauthorized - JWT auth issue detected")
        print(f"    [ANALYSIS] Error message: {response_data.get('detail', response_data)}")
    sys.exit(1)

print("\n" + "="*70)
print("ALL TESTS PASSED")
print("="*70 + "\n")
