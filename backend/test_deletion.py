"""
Event Deletion Testing Utility
Tests the delete functionality with and without interested users
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Event

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def create_test_users():
    """Create test users for testing"""
    print_section("Creating Test Users")
    
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'test1@example.com',
            'first_name': 'Test',
            'last_name': 'User 1',
        }
    )
    if created:
        user1.set_password('testpass123')
        user1.save()
        print(f"✅ Created user: {user1.username}")
    else:
        print(f"⚠️  User already exists: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username='testuser2',
        defaults={
            'email': 'test2@example.com',
            'first_name': 'Test',
            'last_name': 'User 2',
        }
    )
    if created:
        user2.set_password('testpass123')
        user2.save()
        print(f"✅ Created user: {user2.username}")
    else:
        print(f"⚠️  User already exists: {user2.username}")
    
    return user1, user2

def create_test_events(user1, user2):
    """Create test events"""
    print_section("Creating Test Events")
    
    # Event 1: Event without interested users
    event1, created = Event.objects.get_or_create(
        name='Tech Meetup (No RSVP)',
        defaults={
            'description': 'A tech meetup event for testing',
            'date_time': timezone.now() + timedelta(days=7),
            'location': 'Virtual',
            'category': 'Tech',
            'organiser': user1,
        }
    )
    if created:
        print(f"✅ Created event: {event1.name} (ID: {event1.id})")
    else:
        print(f"⚠️  Event already exists: {event1.name}")
    
    # Event 2: Event with interested users
    event2, created = Event.objects.get_or_create(
        name='Sports Event (With RSVPs)',
        defaults={
            'description': 'A sports event with multiple interested users',
            'date_time': timezone.now() + timedelta(days=14),
            'location': 'Stadium',
            'category': 'Sports',
            'organiser': user1,
        }
    )
    if created:
        print(f"✅ Created event: {event2.name} (ID: {event2.id})")
    else:
        print(f"⚠️  Event already exists: {event2.name}")
    
    # Add interested users to event2
    if user2 not in event2.interested_users.all():
        event2.interested_users.add(user2)
        print(f"✅ Added {user2.username} to event {event2.name}")
    
    return event1, event2

def print_event_info(event):
    """Print detailed event information"""
    interested_count = event.interested_users.count()
    interested_users = ', '.join([u.username for u in event.interested_users.all()])
    
    print(f"📋 Event: {event.name}")
    print(f"   ID: {event.id}")
    print(f"   Organiser: {event.organiser.username}")
    print(f"   Date: {event.date_time}")
    print(f"   Location: {event.location}")
    print(f"   Category: {event.category}")
    print(f"   Interested Users: {interested_count}")
    if interested_count > 0:
        print(f"   Users: {interested_users}")
    print()

def test_deletion(event, simulate=True):
    """Test event deletion"""
    print_section(f"Testing Deletion of: {event.name}")
    
    print_event_info(event)
    
    if simulate:
        # Simulate what would happen
        interested_count = event.interested_users.count()
        print(f"🔍 Before deletion:")
        print(f"   Event exists: {Event.objects.filter(id=event.id).exists()}")
        print(f"   Interested users: {interested_count}")
        print()
        
        # Simulate deletion (without actually deleting)
        print(f"🧪 Simulating deletion...")
        print(f"   Would delete Event: {event.name} (ID: {event.id})")
        print(f"   Would clear {interested_count} interested user relationships")
        print()
    else:
        # Actually delete
        event_id = event.id
        event_name = event.name
        interested_count = event.interested_users.count()
        
        print(f"🔴 ACTUALLY DELETING: {event_name} (ID: {event_id})")
        print(f"   Will clear {interested_count} interested user relationships")
        
        event.delete()
        
        print(f"✅ Deletion completed")
        print(f"   Event exists now: {Event.objects.filter(id=event_id).exists()}")

def print_all_events():
    """Print all events in database"""
    print_section("All Events in Database")
    
    events = Event.objects.all()
    if not events.exists():
        print("No events found\n")
        return
    
    for event in events:
        print_event_info(event)

def main():
    """Run the test suite"""
    print("\n" + "="*60)
    print("  Event Deletion Testing Utility")
    print("="*60)
    
    # Create test users
    user1, user2 = create_test_users()
    
    # Show initial state
    print_all_events()
    
    # Create test events
    event1, event2 = create_test_events(user1, user2)
    
    # Show events after creation
    print_all_events()
    
    # Test deletion (simulate)
    print("\n" + "-"*60)
    print("SIMULATION TEST - Events will not be deleted")
    print("-"*60)
    
    test_deletion(event1, simulate=True)
    test_deletion(event2, simulate=True)
    
    # Instructions
    print_section("How to Actually Test the Deletion")
    print("""
To test deletion in the actual application:

1. Start the development server:
   python manage.py runserver

2. Open browser: http://localhost:8000/login

3. Login as testuser1 / testpass123

4. Go to /dashboard

5. You should see the two test events:
   - Tech Meetup (No RSVP)
   - Sports Event (With RSVPs)

6. Click Delete on Tech Meetup first
   - Check browser console for [DELETE] logs
   - Should see: "Event deleted successfully!"
   - Event should disappear

7. Click Delete on Sports Event
   - Check browser console for [DELETE] logs
   - Should see log: "Event has 1 interested users"
   - Should still succeed even with interested users
   - Check: "interested_users_removed": 1

8. Check this script output to verify deletion:
   python test_deletion.py

Common things to check:
✅ Browser console shows [DELETE] and [LOAD] logs
✅ Network tab shows DELETE request returns 200 status
✅ Response body shows "success": true
✅ Events reload after deletion
✅ Error messages are clear if anything fails
    """)
    
    print_all_events()

if __name__ == '__main__':
    main()
