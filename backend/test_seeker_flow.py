import requests

BASE = 'http://127.0.0.1:8000'

print("=" * 60)
print("SEEKER (ATTENDING) FLOW TEST")
print("=" * 60)

# Use a session to track cookies (like a browser)
session = requests.Session()

# 1. Register as Seeker
print("\n[1] Register as Seeker (Attending)")
r1 = session.post(f'{BASE}/api/register/', json={
    'username': 'attend_user1',
    'email': 'attend1@test.com',
    'password': 'TestPass123!',
    'first_name': 'Alice',
    'last_name': 'Attend',
    'role': 'Seeker'
})
print(f"    Status: {r1.status_code}")
if r1.status_code != 201:
    print(f"    Error: {r1.json()}")
    exit(1)
data = r1.json()
token = data['access']
print(f"    Role: {data['role']}")
print(f"    Username: {data['user']['username']}")
print("    PASS")

# 2. Access seeker dashboard with token (first visit)
print("\n[2] Access seeker-dashboard with token (first visit)")
r2 = session.get(f'{BASE}/seeker-dashboard?token={token}')
print(f"    Status: {r2.status_code}")
print(f"    URL: {r2.url}")
has_content = 'Attending Events' in r2.text
print(f"    Has 'Attending Events': {has_content}")
# Check if session cookie was set
session_cookie = session.cookies.get('sessionid')
print(f"    Session cookie set: {bool(session_cookie)}")
if has_content:
    print("    PASS")
else:
    print("    FAIL")

# 3. Access seeker dashboard WITHOUT token (session-based)
print("\n[3] Access seeker-dashboard WITHOUT token (session auth)")
r3 = session.get(f'{BASE}/seeker-dashboard')
print(f"    Status: {r3.status_code}")
print(f"    URL: {r3.url}")
still_dashboard = 'Attending Events' in r3.text
redirected_to_login = 'login' in r3.url.lower() or 'Sign in' in r3.text
print(f"    Still on dashboard: {still_dashboard}")
print(f"    Redirected to login: {redirected_to_login}")
if still_dashboard:
    print("    PASS - Session auth works!")
else:
    print("    FAIL - Session not persisted!")

# 4. Access create-event page (should work with session)
print("\n[4] Access create-event page (session auth)")
r4 = session.get(f'{BASE}/create-event')
print(f"    Status: {r4.status_code}")
has_form = 'createEventForm' in r4.text
print(f"    Has create event form: {has_form}")
if has_form:
    print("    PASS")
else:
    print("    FAIL")

# 5. Also register an Organizer and create an event so seeker has events to see
print("\n[5] Register Organizer + Create Event for seeker to see")
org_session = requests.Session()
r5 = org_session.post(f'{BASE}/api/register/', json={
    'username': 'org_user1',
    'email': 'org1@test.com',
    'password': 'TestPass123!',
    'first_name': 'Bob',
    'last_name': 'Organizer',
    'role': 'Organizer'
})
print(f"    Register Organizer: {r5.status_code}")
org_data = r5.json()
org_token = org_data['access']

# Create an event
headers = {'Authorization': f'Bearer {org_token}', 'Content-Type': 'application/json'}
r6 = requests.post(f'{BASE}/api/events/create/', json={
    'name': 'Tech Conference 2026',
    'description': 'A wonderful technology conference with speakers from around the world.',
    'date_time': '2026-12-15T10:00:00',
    'location': 'Convention Center, New York',
    'category': 'Tech',
    'ticket_price': 50.00
}, headers=headers)
print(f"    Create Event: {r6.status_code}")

r7 = requests.post(f'{BASE}/api/events/create/', json={
    'name': 'Art Gallery Opening Night',
    'description': 'Join us for the grand opening of the new art gallery featuring modern artists.',
    'date_time': '2026-11-20T18:00:00',
    'location': 'Downtown Art Gallery',
    'category': 'Arts',
    'ticket_price': 25.00
}, headers=headers)
print(f"    Create Event 2: {r7.status_code}")

# 6. Now check seeker can see events
print("\n[6] Seeker fetches public events")
r8 = session.get(f'{BASE}/api/events/')
print(f"    Status: {r8.status_code}")
ev_data = r8.json()
print(f"    Events count: {ev_data.get('count')}")
for ev in ev_data.get('events', []):
    print(f"    - {ev['name']} (by {ev.get('organiser_name', 'Unknown')})")
if ev_data.get('count', 0) > 0:
    print("    PASS")
else:
    print("    FAIL - No events visible")

# 7. Test dashboard reload (should still work with session)
print("\n[7] Reload seeker dashboard (verify session persists)")
r9 = session.get(f'{BASE}/seeker-dashboard')
print(f"    Status: {r9.status_code}")
has_dashboard = 'Attending Events' in r9.text
has_username = 'attend_user1' in r9.text
print(f"    Dashboard loaded: {has_dashboard}")
print(f"    Shows username: {has_username}")
if has_dashboard:
    print("    PASS")
else:
    print("    FAIL")

print("\n" + "=" * 60)
print("ALL SEEKER TESTS COMPLETE")
print("=" * 60)
