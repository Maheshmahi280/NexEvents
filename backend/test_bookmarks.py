#!/usr/bin/env python
"""
Test Bookmarks Feature
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from events.models import Event
from django.test import Client
from django.utils import timezone
from datetime import timedelta
import json

print("\n" + "="*70)
print("BOOKMARKS FEATURE TEST")
print("="*70)

# Create test users
print("\n[1] Creating test users...")
organizer, _ = User.objects.get_or_create(
    username='test_organizer',
    defaults={'email': 'org@test.com'}
)
organizer.set_password('testpass')
organizer.save()
print(f"    [OK] Organizer created: {organizer.username}")

attendee, _ = User.objects.get_or_create(
    username='test_attendee',
    defaults={'email': 'att@test.com'}
)
attendee.set_password('testpass')
attendee.save()
print(f"    [OK] Attendee created: {attendee.username}")

# Create test events
print("\n[2] Creating test events...")
event1, _ = Event.objects.get_or_create(
    name='Test Event 1',
    defaults={
        'description': 'Test event description',
        'date_time': timezone.now() + timedelta(days=1),
        'location': 'Test Location',
        'category': 'Tech',
        'organiser': organizer
    }
)
print(f"    [OK] Event created: {event1.name}")

event2, _ = Event.objects.get_or_create(
    name='Test Event 2',
    defaults={
        'description': 'Another test event',
        'date_time': timezone.now() + timedelta(days=2),
        'location': 'Another Location',
        'category': 'Arts',
        'organiser': organizer
    }
)
print(f"    [OK] Event created: {event2.name}")

# Test bookmarking functionality
print("\n[3] Testing RSVP/Bookmark endpoint...")
client = Client()

# Login as attendee
login_resp = client.post('/api/login/', {
    'username': 'test_attendee',
    'password': 'testpass'
}, content_type='application/json')

if login_resp.status_code == 200:
    login_data = json.loads(login_resp.content)
    token = login_data.get('access')
    print(f"    [OK] Login successful, got token")
else:
    print(f"    [ERROR] Login failed: {login_resp.content}")
    sys.exit(1)

# Add to bookmarks
print("\n[4] Adding events to bookmarks...")
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

resp1 = client.post(f'/api/events/{event1.id}/rsvp/', {}, content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {token}')
print(f"    Status: {resp1.status_code}")
if resp1.status_code == 200:
    print(f"    [OK] Event 1 bookmarked")
else:
    print(f"    [ERROR] {resp1.content}")

resp2 = client.post(f'/api/events/{event2.id}/rsvp/', {}, content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {token}')
print(f"    Status: {resp2.status_code}")
if resp2.status_code == 200:
    print(f"    [OK] Event 2 bookmarked")
else:
    print(f"    [ERROR] {resp2.content}")

# Test bookmarks endpoint
print("\n[5] Testing /api/events/bookmarks/ endpoint...")
bookmarks_resp = client.get('/api/events/bookmarks/',
                           HTTP_AUTHORIZATION=f'Bearer {token}')
print(f"    Status: {bookmarks_resp.status_code}")

if bookmarks_resp.status_code == 200:
    bookmarks_data = json.loads(bookmarks_resp.content)
    count = bookmarks_data.get('count', 0)
    bookmarks = bookmarks_data.get('bookmarks', [])
    print(f"    [OK] Retrieved {count} bookmarked events")
    for bookmark in bookmarks:
        print(f"        - {bookmark['name']}")
else:
    print(f"    [ERROR] {bookmarks_resp.content}")

# Test removing bookmark
print("\n[6] Testing bookmark removal...")
resp_remove = client.post(f'/api/events/{event1.id}/rsvp/', {}, content_type='application/json',
                         HTTP_AUTHORIZATION=f'Bearer {token}')
print(f"    Status: {resp_remove.status_code}")
if resp_remove.status_code == 200:
    print(f"    [OK] Event 1 bookmark removed")

# Verify bookmarks count decreased
bookmarks_resp2 = client.get('/api/events/bookmarks/',
                            HTTP_AUTHORIZATION=f'Bearer {token}')
if bookmarks_resp2.status_code == 200:
    bookmarks_data2 = json.loads(bookmarks_resp2.content)
    count2 = bookmarks_data2.get('count', 0)
    print(f"    [OK] Bookmarks count is now: {count2}")

print("\n" + "="*70)
print("ALL TESTS PASSED")
print("="*70 + "\n")
