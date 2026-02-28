import requests

BASE = 'http://127.0.0.1:8000'

# 1. Test attending join page
r = requests.get(f'{BASE}/join/attending')
print(f'1. Attending join page: {r.status_code}, URL: {r.url}')

# 2. Test register page with Seeker role
r2 = requests.get(f'{BASE}/register?role=Seeker')
print(f'2. Register page (Seeker): {r2.status_code}')
has_seeker = 'Seeker' in r2.text
print(f'   Has Seeker role: {has_seeker}')

# 3. Register a seeker user
r3 = requests.post(f'{BASE}/api/register/', json={
    'username': 'seekertest1',
    'email': 'seeker1@test.com',
    'password': 'TestPass123!',
    'first_name': 'Seeker',
    'last_name': 'Test',
    'role': 'Seeker'
})
print(f'3. Register API: {r3.status_code}')
data = r3.json()
print(f'   Response: {data}')

if r3.status_code == 201:
    token = data['access']
    role = data.get('role')
    print(f'   Role: {role}')
    
    # 4. Access seeker dashboard
    r4 = requests.get(f'{BASE}/seeker-dashboard?token={token}')
    print(f'4. Seeker dashboard: {r4.status_code}, URL: {r4.url}')
    has_content = 'Attending Events' in r4.text
    has_js = 'loadSeekerEvents' in r4.text
    print(f'   Has dashboard content: {has_content}')
    print(f'   Has JS loadSeekerEvents: {has_js}')
    
    # 5. Check events API (public)
    headers = {'Authorization': f'Bearer {token}'}
    r5 = requests.get(f'{BASE}/api/events/', headers=headers)
    print(f'5. Events API: {r5.status_code}')
    ev_data = r5.json()
    print(f'   Events count: {ev_data.get("count")}')
    print(f'   Message: {ev_data.get("message")}')

    # 6. Check if base.html loaded properly
    has_bootstrap = 'bootstrap' in r4.text.lower()
    has_font_awesome = 'font-awesome' in r4.text.lower() or 'fontawesome' in r4.text.lower()
    print(f'6. Has Bootstrap: {has_bootstrap}')
    print(f'   Has Font Awesome: {has_font_awesome}')
    
    # 7. Login test
    r7 = requests.post(f'{BASE}/api/login/', json={
        'username': 'seekertest1',
        'password': 'TestPass123!'
    })
    print(f'7. Login API: {r7.status_code}')
    login_data = r7.json()
    print(f'   Role: {login_data.get("role")}')
else:
    print(f'   FAILED: {data}')
