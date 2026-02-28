#!/usr/bin/env python
"""Test JWT authentication flow"""
import os
import sys
import django

# Set up the path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import time

# Create a test user
username = f'testuser_{int(time.time())}'
user = User.objects.create_user(
    username=username,
    email=f'{username}@test.com',
    password='testpass123',
    first_name='Test',
    last_name='User'
)

# Create profile with role
from events.models import UserProfile
if not hasattr(user, 'profile'):
    profile = UserProfile.objects.create(user=user, role='Seeker')
else:
    user.profile.role = 'Seeker'
    user.profile.save()

# Generate token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

print(f"✓ Test User Created: {username}")
print(f"✓ Access Token: {access_token[:50]}...")
print(f"✓ User ID: {user.id}")
print(f"✓ User Role: {user.profile.role}")

# Test JWT authentication with token
print("\n--- Testing JWT Authentication ---")
class FakeRequest:
    def __init__(self, token):
        self.META = {
            'HTTP_AUTHORIZATION': f'Bearer {token}'
        }

try:
    auth = JWTAuthentication()
    request = FakeRequest(access_token)
    result = auth.authenticate(request)
    
    if result:
        authenticated_user, validated_token = result
        print(f"✓ JWT Authentication Success!")
        print(f"  - Authenticated User: {authenticated_user.username}")
        print(f"  - User ID: {authenticated_user.id}")
        print(f"  - User Role: {authenticated_user.profile.role if hasattr(authenticated_user, 'profile') else 'No profile'}")
    else:
        print("✗ JWT Authentication returned None")
        
except AuthenticationFailed as e:
    print(f"✗ JWT Authentication Failed: {e}")
except Exception as e:
    print(f"✗ Unexpected Error: {type(e).__name__}: {e}")

print("\n--- Testing Dashboard Route ---")
print(f"URL to test: /seeker-dashboard?token={access_token[:20]}...")
