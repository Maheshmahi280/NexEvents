#!/usr/bin/env python
"""
Test script for role-based authentication flows
"""
import os
import django
import json
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def cleanup_test_users():
    """Delete test users if they exist"""
    # Delete users (cascade should delete profiles)
    User.objects.filter(username__in=['seeker_test', 'organizer_test']).delete()

def create_test_users():
    """Create test users for both roles"""
    # Create Seeker user
    seeker_user, _ = User.objects.get_or_create(
        username='seeker_test',
        defaults={
            'email': 'seeker@test.com',
            'first_name': 'John',
            'last_name': 'Attendee'
        }
    )
    if seeker_user.email != 'seeker@test.com':
        seeker_user.email = 'seeker@test.com'
        seeker_user.first_name = 'John'
        seeker_user.last_name = 'Attendee'
        seeker_user.set_password('TestPassword123')
        seeker_user.save()
    else:
        seeker_user.set_password('TestPassword123')
        seeker_user.save()
    
    # Get or create profile
    seeker_profile, _ = UserProfile.objects.get_or_create(
        user=seeker_user,
        defaults={'role': 'Seeker'}
    )
    
    # Create Organizer user
    organizer_user, _ = User.objects.get_or_create(
        username='organizer_test',
        defaults={
            'email': 'organizer@test.com',
            'first_name': 'Jane',
            'last_name': 'Organizer'
        }
    )
    if organizer_user.email != 'organizer@test.com':
        organizer_user.email = 'organizer@test.com'
        organizer_user.first_name = 'Jane'
        organizer_user.last_name = 'Organizer'
        organizer_user.set_password('TestPassword123')
        organizer_user.save()
    else:
        organizer_user.set_password('TestPassword123')
        organizer_user.save()
    
    # Get or create profile
    organizer_profile, _ = UserProfile.objects.get_or_create(
        user=organizer_user,
        defaults={'role': 'Organizer'}
    )
    
    print("✓ Created test users successfully")
    return seeker_user, organizer_user

def test_role_specific_registration_pages():
    """Test that role-specific registration pages display correctly"""
    client = Client()
    
    print("\n=== Testing Role-Specific Registration Pages ===")
    
    # Test /join/attending
    response = client.get('/join/attending')
    print(f"GET /join/attending: {response.status_code}")
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if "You're signing up as: Attendee" in content and "Attending Events" in content:
            print("✓ Attendee page shows role-specific content")
        else:
            print("✗ Attendee page missing role-specific content")
    
    # Test /join/organizing
    response = client.get('/join/organizing')
    print(f"GET /join/organizing: {response.status_code}")
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if "You're signing up as: Organizer" in content and "Organizing Events" in content:
            print("✓ Organizer page shows role-specific content")
        else:
            print("✗ Organizer page missing role-specific content")
    
    # Test generic /register (should show role selection)
    response = client.get('/register')
    print(f"GET /register: {response.status_code}")
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if "I'm interested in" in content:
            print("✓ Generic register page shows role selection")
        else:
            print("✗ Generic register page missing role selection")

def test_login_flow():
    """Test login functionality"""
    client = Client()
    
    print("\n=== Testing Login Flow ===")
    
    # Test login with Seeker credentials
    response = client.post('/api/login/', {
        'username': 'seeker_test',
        'password': 'TestPassword123'
    }, content_type='application/json')
    
    print(f"POST /api/login/ (Seeker): {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('role') == 'Seeker':
            print("✓ Seeker login returns correct role")
        else:
            print(f"✗ Seeker login returned role: {data.get('role')}")
    else:
        print(f"✗ Login failed: {response.content}")

def test_dashboard_access_control():
    """Test that dashboard access is properly restricted"""
    client = Client()
    
    print("\n=== Testing Dashboard Access Control ===")
    
    # Login as Seeker
    response = client.post('/api/login/', {
        'username': 'seeker_test',
        'password': 'TestPassword123'
    }, content_type='application/json')
    
    if response.status_code == 200:
        access_token = json.loads(response.content)['access']
        
        # Seeker accessing seeker-dashboard (should work)
        response = client.get(
            '/seeker-dashboard',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        print(f"Seeker GET /seeker-dashboard: {response.status_code}")
        if response.status_code == 200:
            print("✓ Seeker can access seeker-dashboard")
        else:
            print(f"✗ Seeker cannot access seeker-dashboard: {response.status_code}")
        
        # Seeker accessing organizer-dashboard (should redirect)
        response = client.get(
            '/organizer-dashboard',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        print(f"Seeker GET /organizer-dashboard: {response.status_code}")
        if response.status_code == 302:  # Redirect
            print("✓ Seeker redirected from organizer-dashboard")
        else:
            print(f"✗ Unexpected status for seeker on organizer dashboard: {response.status_code}")
    
    # Login as Organizer
    response = client.post('/api/login/', {
        'username': 'organizer_test',
        'password': 'TestPassword123'
    }, content_type='application/json')
    
    if response.status_code == 200:
        access_token = json.loads(response.content)['access']
        
        # Organizer accessing organizer-dashboard (should work)
        response = client.get(
            '/organizer-dashboard',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        print(f"Organizer GET /organizer-dashboard: {response.status_code}")
        if response.status_code == 200:
            print("✓ Organizer can access organizer-dashboard")
        else:
            print(f"✗ Organizer cannot access organizer-dashboard: {response.status_code}")
        
        # Organizer accessing seeker-dashboard (should redirect)
        response = client.get(
            '/seeker-dashboard',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        print(f"Organizer GET /seeker-dashboard: {response.status_code}")
        if response.status_code == 302:  # Redirect
            print("✓ Organizer redirected from seeker-dashboard")
        else:
            print(f"✗ Unexpected status for organizer on seeker dashboard: {response.status_code}")

def main():
    print("=" * 50)
    print("ROLE-BASED AUTHENTICATION TESTS")
    print("=" * 50)
    
    try:
        # Setup: cleanup old test users
        cleanup_test_users()
        
        # Create test users
        seeker_user, organizer_user = create_test_users()
        
        # Run tests
        test_role_specific_registration_pages()
        test_login_flow()
        test_dashboard_access_control()
        
        print("\n" + "=" * 50)
        print("TESTS COMPLETED")
        print("=" * 50)
        
    finally:
        # Cleanup
        cleanup_test_users()
        print("\n✓ Cleanup: Test users removed")

if __name__ == '__main__':
    main()
