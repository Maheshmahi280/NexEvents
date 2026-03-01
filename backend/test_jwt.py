"""
Test JWT Token Generation and Validation
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import status
from django.test import RequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

print("="*60)
print("JWT Token Generation and Validation Test")
print("="*60)

# Create or get test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"\n[OK] Created test user: {user.username}")
else:
    print(f"\n[OK] Using existing test user: {user.username}")

# Generate RefreshToken and AccessToken
print("\n1. Generating tokens...")
refresh = RefreshToken.for_user(user)
access_token_str = str(refresh.access_token)
refresh_token_str = str(refresh)

print(f"[OK] Generated RefreshToken")
print(f"[OK] Generated AccessToken")

# Decode and print token claims
import jwt
from django.conf import settings

print("\n2. Token Claims:")
print("\nAccessToken claims:")
access_payload = jwt.decode(access_token_str, settings.SECRET_KEY, algorithms=['HS256'])
for key, value in access_payload.items():
    if key != 'user_id':
        print(f"  {key}: {value}")

print("\nRefreshToken claims:")
refresh_payload = jwt.decode(refresh_token_str, settings.SECRET_KEY, algorithms=['HS256'])
for key, value in refresh_payload.items():
    if key != 'user_id':
        print(f"  {key}: {value}")

# Try to authenticate with AccessToken
print("\n3. Testing JWT Authentication with AccessToken...")
factory = RequestFactory()

# Create request with Bearer token
request = factory.get('/', HTTP_AUTHORIZATION=f'Bearer {access_token_str}')

# Try authentication
auth = JWTAuthentication()
try:
    result = auth.authenticate(request)
    if result:
        authenticated_user, token = result
        print(f"[OK] Authentication successful!")
        print(f"   User: {authenticated_user.username}")
        print(f"   Token class: {token.__class__.__name__}")
    else:
        print(f"[WARNING] auth.authenticate() returned None")
except InvalidToken as e:
    print(f"[ERROR] InvalidToken Exception: {str(e)}")
except Exception as e:
    print(f"[ERROR] Other Exception: {type(e).__name__}: {str(e)}")

# Try with the actual token string from login response
print("\n4. Token Strings Generated:")
print(f"AccessToken: {access_token_str[:50]}...")
print(f"Length: {len(access_token_str)} characters")

print("\n" + "="*60)
print("Test Complete")
print("="*60)
