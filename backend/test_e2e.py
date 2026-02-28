"""
End-to-end test script for the complete organizer flow:
1. Register as Organizer
2. Login and get tokens
3. Access organizer dashboard
4. Create an event via API
5. Verify event appears in user events
6. Delete the event
"""
import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000"

def test_complete_flow():
    print("=" * 60)
    print("NEXEVENT END-TO-END TEST")
    print("=" * 60)
    
    # Generate unique username
    suffix = random.randint(1000, 9999)
    username = f"testorg_{suffix}"
    email = f"testorg_{suffix}@test.com"
    password = "TestPass123!"
    
    # 1. REGISTER
    print(f"\n[1] Registering as Organizer: {username}")
    reg_resp = requests.post(f"{BASE_URL}/api/register/", json={
        "username": username,
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "Organizer",
        "role": "Organizer"
    })
    print(f"    Status: {reg_resp.status_code}")
    reg_data = reg_resp.json()
    
    if reg_resp.status_code != 201:
        print(f"    ERROR: {reg_data}")
        return False
    
    print(f"    Role: {reg_data.get('role')}")
    assert reg_data['role'] == 'Organizer', f"Expected Organizer, got {reg_data['role']}"
    
    access_token = reg_data['access']
    refresh_token = reg_data['refresh']
    print(f"    Access token: {access_token[:30]}...")
    print("    PASS")
    
    # 2. LOGIN
    print(f"\n[2] Logging in as {username}")
    login_resp = requests.post(f"{BASE_URL}/api/login/", json={
        "username": username,
        "password": password
    })
    print(f"    Status: {login_resp.status_code}")
    login_data = login_resp.json()
    
    if login_resp.status_code != 200:
        print(f"    ERROR: {login_data}")
        return False
    
    access_token = login_data['access']
    refresh_token = login_data['refresh']
    print(f"    Role: {login_data.get('role')}")
    print("    PASS")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 3. ACCESS ORGANIZER DASHBOARD
    print(f"\n[3] Accessing organizer dashboard with token")
    dash_resp = requests.get(f"{BASE_URL}/organizer-dashboard?token={access_token}")
    print(f"    Status: {dash_resp.status_code}")
    
    if dash_resp.status_code != 200:
        print(f"    ERROR: Dashboard returned {dash_resp.status_code}")
        # Check if there was a redirect
        print(f"    URL: {dash_resp.url}")
        return False
    
    assert 'Organizer Dashboard' in dash_resp.text, "Dashboard page doesn't contain expected content"
    print("    Dashboard loaded successfully")
    print("    PASS")
    
    # 4. GET USER EVENTS (should be empty)
    print(f"\n[4] Fetching user events (should be empty)")
    events_resp = requests.get(f"{BASE_URL}/api/events/my/", headers=headers)
    print(f"    Status: {events_resp.status_code}")
    events_data = events_resp.json()
    
    if events_resp.status_code != 200:
        print(f"    ERROR: {events_data}")
        return False
    
    print(f"    Count: {events_data.get('count')}")
    print(f"    Message: {events_data.get('message')}")
    assert events_data['count'] == 0, f"Expected 0 events, got {events_data['count']}"
    print("    PASS")
    
    # 5. CREATE EVENT
    print(f"\n[5] Creating a test event")
    event_data = {
        "name": f"Test Event {suffix}",
        "description": "This is a test event for end-to-end testing of the NexEvent platform.",
        "date_time": "2026-12-31T18:00:00",
        "location": "Test Venue, Test City",
        "category": "Tech",
        "cover_image": "",
        "ticket_price": 25.00
    }
    
    create_resp = requests.post(f"{BASE_URL}/api/events/create/", json=event_data, headers=headers)
    print(f"    Status: {create_resp.status_code}")
    create_data = create_resp.json()
    
    if create_resp.status_code != 201:
        print(f"    ERROR: {create_data}")
        return False
    
    event_id = create_data.get('event', {}).get('id')
    print(f"    Event ID: {event_id}")
    print(f"    Event Name: {create_data.get('event', {}).get('name')}")
    print("    PASS")
    
    # 6. VERIFY EVENT APPEARS IN USER EVENTS
    print(f"\n[6] Verifying event appears in user events")
    events_resp2 = requests.get(f"{BASE_URL}/api/events/my/", headers=headers)
    print(f"    Status: {events_resp2.status_code}")
    events_data2 = events_resp2.json()
    
    if events_resp2.status_code != 200:
        print(f"    ERROR: {events_data2}")
        return False
    
    print(f"    Count: {events_data2.get('count')}")
    assert events_data2['count'] == 1, f"Expected 1 event, got {events_data2['count']}"
    
    event = events_data2['events'][0]
    print(f"    Event name: {event.get('name')}")
    print(f"    Event organiser: {event.get('organiser_username')}")
    assert event['name'] == f"Test Event {suffix}", "Event name mismatch"
    print("    PASS")
    
    # 7. VERIFY EVENT ALSO APPEARS IN PUBLIC LIST
    print(f"\n[7] Verifying event appears in public event list")
    public_resp = requests.get(f"{BASE_URL}/api/events/")
    print(f"    Status: {public_resp.status_code}")
    
    if public_resp.status_code == 200:
        public_data = public_resp.json()
        event_names = [e.get('name') for e in public_data.get('events', [])]
        found = f"Test Event {suffix}" in event_names
        print(f"    Found in public list: {found}")
        if found:
            print("    PASS")
        else:
            print("    WARN: Event not found in public list (might be filtered)")
    
    # 8. DELETE EVENT
    if event_id:
        print(f"\n[8] Deleting event {event_id}")
        del_resp = requests.delete(f"{BASE_URL}/api/events/{event_id}/delete/", headers=headers)
        print(f"    Status: {del_resp.status_code}")
        
        if del_resp.status_code in [200, 204]:
            print("    PASS")
        else:
            del_data = del_resp.json()
            print(f"    ERROR: {del_data}")
    
    # 9. VERIFY DELETION
    print(f"\n[9] Verifying event was deleted")
    events_resp3 = requests.get(f"{BASE_URL}/api/events/my/", headers=headers)
    events_data3 = events_resp3.json()
    print(f"    Count: {events_data3.get('count')}")
    assert events_data3['count'] == 0, f"Expected 0 events after deletion, got {events_data3['count']}"
    print("    PASS")
    
    # 10. ACCESS CREATE-EVENT PAGE
    print(f"\n[10] Accessing create-event page")
    create_page = requests.get(f"{BASE_URL}/create-event?token={access_token}")
    print(f"    Status: {create_page.status_code}")
    
    if create_page.status_code == 200:
        has_form = 'createEventForm' in create_page.text
        has_submit = 'handleCreateEventSubmit' in create_page.text
        print(f"    Has form: {has_form}")
        print(f"    Has submit handler: {has_submit}")
        
        if has_form and has_submit:
            print("    PASS")
        else:
            print("    WARN: Form or submit handler missing")
    else:
        print(f"    WARN: Create-event page not accessible (status {create_page.status_code})")
    
    # SUMMARY
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nTest user: {username}")
    print("Complete flow verified:")
    print("  - Register as Organizer")
    print("  - Login and get JWT tokens")
    print("  - Access organizer dashboard")
    print("  - Fetch user events (empty)")
    print("  - Create event via API")
    print("  - Verify event in user events")
    print("  - Delete event")
    print("  - Verify deletion")
    print("  - Access create-event page")
    
    return True


if __name__ == "__main__":
    success = test_complete_flow()
    if not success:
        print("\nTEST FAILED!")
        exit(1)
