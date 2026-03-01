#!/usr/bin/env python
"""
Simulate Frontend Request to Event Creation API
Tests with the exact same request headers and data format as the frontend
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
from rest_framework_simplejwt.tokens import RefreshToken

print("\n" + "="*70)
print("FRONTEND REQUEST SIMULATION TEST")
print("="*70)

# Initialize test client
client = Client()

# Create test user
print("\n[1] Creating test user...")
test_user, created = User.objects.get_or_create(
    username='frontendtest',
    defaults={
        'email': 'frontendtest@example.com',
        'first_name': 'Frontend',
        'last_name': 'Test',
    }
)
if created:
    test_user.set_password('frontendtest123')
    test_user.save()
    print(f"    [OK] Created user: {test_user.username}")
else:
    test_user.set_password('frontendtest123')
    test_user.save()
    print(f"    [OK] Using existing user: {test_user.username}")

# Generate access token directly (simulating what the backend returns)
print("\n[2] Generating JWT access token (as backend would)...")
refresh = RefreshToken.for_user(test_user)
access_token = str(refresh.access_token)
print(f"    [OK] Generated token: {access_token[:50]}...")

# Prepare event data exactly as frontend does
print("\n[3] Preparing event data...")
now = timezone.now()
future_time = now + timedelta(days=1)
date_str = future_time.date().isoformat()
time_str = future_time.time().isoformat()[:5]  # HH:MM format
datetime_str = f"{date_str}T{time_str}:00"

event_data = {
    'name': 'Frontend Simulation Event',
    'description': 'This event is created by simulating the exact frontend request',
    'date_time': datetime_str,
    'location': 'Simulation Test Location',
    'category': 'Tech',
    'cover_image': '',
    'ticket_price': 0
}

print(f"    Event: {event_data['name']}")
print(f"    DateTime: {datetime_str}")

# Make request with Bearer token (exactly as frontend does)
print("\n[4] Sending request to /api/events/create/ endpoint...")
print(f"    Authorization: Bearer {access_token[:50]}...")

response = client.post(
    '/api/events/create/',
    data=json.dumps(event_data),
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {access_token}'
)

print(f"    Response Status: {response.status_code}")

response_data = json.loads(response.content)

if response.status_code == 201:
    print(f"\n    [SUCCESS] Event created successfully!")
    print(f"    Event ID: {response_data.get('event', {}).get('id')}")
    print(f"    Event name: {response_data.get('event', {}).get('name')}")
    print("\n    TEST PASSED: Frontend request works correctly!")
elif response.status_code == 401:
    print(f"\n    [FAILURE] Authentication failed!")
    print(f"    Response: {response_data}")
    print(f"\n    [ANALYSIS]")
    print(f"    - Token was not accepted")
    print(f"    - Error detail: {response_data.get('detail', 'No detail provided')}")
else:
    print(f"\n    [ERROR] Unexpected status code: {response.status_code}")
    print(f"    Response: {response_data}")

print("\n" + "="*70 + "\n")
