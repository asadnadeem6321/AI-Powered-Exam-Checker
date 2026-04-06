"""
Test Cases for User Authentication and Management
Location: tests/test_users.py
"""
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from rest_framework import status
import json


class UserRegistrationTestCase(TestCase):
    """Test user registration functionality"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.valid_data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password': 'securepass123!',
            'password_confirm': 'securepass123!',
        }
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.json())
        self.assertIn('access', response.json()['tokens'])
        self.assertIn('refresh', response.json()['tokens'])
        
        # Verify user was created
        user = User.objects.get(email=self.valid_data['email'])
        self.assertEqual(user.name, self.valid_data['name'])
    
    def test_registration_missing_field(self):
        """Test registration with missing field"""
        invalid_data = {
            'email': 'test@example.com',
            'password': 'securepass123!',
            'password_confirm': 'securepass123!',
        }
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        invalid_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'securepass123!',
            'password_confirm': 'differentpass123!',
        }
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        User.objects.create_user(
            email='duplicate@example.com',
            name='Existing User',
            password='password123!'
        )
        
        # Try to register with same email
        duplicate_data = {
            'email': 'duplicate@example.com',
            'name': 'Another User',
            'password': 'securepass123!',
            'password_confirm': 'securepass123!',
        }
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(TestCase):
    """Test user login functionality"""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('users:login')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='securepass123!'
        )
    
    def test_login_success(self):
        """Test successful login"""
        login_data = {
            'email': 'testuser@example.com',
            'password': 'securepass123!'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.json())
        self.assertIn('user', response.json())
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTestCase(TestCase):
    """Test user profile endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('users:profile')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='securepass123!'
        )
        
        # Login to get token
        login_response = self.client.post(
            reverse('users:login'),
            data=json.dumps({
                'email': 'testuser@example.com',
                'password': 'securepass123!'
            }),
            content_type='application/json'
        )
        self.token = login_response.json()['tokens']['access']
    
    def test_profile_authenticated(self):
        """Test profile view for authenticated user"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        response = self.client.get(self.profile_url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user']['email'], 'testuser@example.com')
    
    def test_profile_unauthenticated(self):
        """Test profile view without authentication"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
