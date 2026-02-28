#!/usr/bin/env python
"""
Test complete registration and dashboard redirect flow
"""
import os
import sys
import django
import json
import requests
from time import time

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Add both the root and backend to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)
sys.path.insert(0, root_path)

# Change to backend directory
os.chdir(backend_path)

django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

# Clean up any test users
test_username = f'regtest_{int(time())}'
User.objects.filter(username=test_username).delete()

# Test data
test_data = {
    'username': test_username,
    'email': f'{test_username}@test.com',
    'password': 'TestPass123!',
    'first_name': 'Test',
    'last_name': 'User',
    'role': 'Seeker'
}

print("=" * 60)
print("TESTING REGISTRATION AND REDIRECT FLOW")
print("=" * 60)

# Test 1: Register via API
print("\n1. Testing Registration API endpoint...")
try:
    response = requests.post(
        'http://localhost:8000/api/register/',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        access_token = data.get('access')
        role = data.get('role')
        user_id = data.get('user', {}).get('id')
        
        print(f"   ✓ Registration successful!")
        print(f"   - User ID: {user_id}")
        print(f"   - Role: {role}")
        print(f"   - Token: {access_token[:50]}...")
        
        # Test 2: Verify dashboard redirect with token
        print("\n2. Testing Dashboard Redirect with JWT Token...")
        
        if role == 'Seeker':
            dashboard_url = f'/seeker-dashboard?token={access_token}'
        else:
            dashboard_url = f'/organizer-dashboard?token={access_token}'
        
        print(f"   Redirect URL: {dashboard_url}")
        
        # Access dashboard with token
        response = requests.get(
            f'http://localhost:8000{dashboard_url}',
            allow_redirects=False,
            headers={'Cookie': ''}  # No session cookie
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ Dashboard authentication successful!")
            print(f"   - Dashboard page loaded without redirect")
        elif response.status_code == 302:
            redirect_location = response.headers.get('Location', 'Unknown')
            print(f"   ✗ Redirected to: {redirect_location}")
            if 'login' in redirect_location:
                print(f"   ! User redirected to login - JWT authentication failed")
            else:
                print(f"   ! User redirected to: {redirect_location}")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            
        # Test 3: Verify user was created with correct role
        print("\n3. Verifying User Database...")
        user = User.objects.get(username=test_username)
        print(f"   ✓ User found in database")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - First Name: {user.first_name}")
        
        if hasattr(user, 'profile'):
            print(f"   - Profile Role: {user.profile.role}")
        else:
            print(f"   - No profile found!")
            
    else:
        print(f"   ✗ Registration failed!")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
