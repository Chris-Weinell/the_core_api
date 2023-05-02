"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.test import APIClient
from rest_framework import status

from datetime import datetime, timedelta
import json

CREATE_USER_URL = reverse('user:create')
TOKEN_OBTAIN_URL = reverse('user:token_obtain')
TOKEN_REFRESH_URL = reverse('user:token_refresh')
ME_URL = reverse('user:me')

def create_user(**args):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**args)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 8 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_jwt_for_user(self):
        """Tests generates JSON Web Token for valid credentials"""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_OBTAIN_URL, payload)

        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_jwt_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {
            'email': 'test@example.com',
            'password': 'badpass'
        }
        res = self.client.post(TOKEN_OBTAIN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_jwt_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_OBTAIN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name': 'Updated name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_refresh_generates_new_jwt(self):
        """Test Refresh Token provides new Refresh and Access Tokens"""
        payload_obtain = {
            'email': self.user.email,
            'password': 'testpass123',
        }
        res_obtain = self.client.post(TOKEN_OBTAIN_URL, payload_obtain)
        refresh_token_one = res_obtain.data['refresh']
        access_token_one = res_obtain.data['access']

        payload_refresh = {
            'refresh': refresh_token_one,
        }
        res_refresh = self.client.post(TOKEN_REFRESH_URL, payload_refresh)
        refresh_token_two = res_refresh.data['refresh']
        access_token_two = res_refresh.data['access']

        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)
        self.assertNotEqual(refresh_token_one, refresh_token_two)
        self.assertNotEqual(access_token_one, access_token_two)

    def test_refresh_jwt_expires(self):
        """Test that Refresh Token can only be used one time."""
        payload_obtain = {
            'email': self.user.email,
            'password': 'testpass123',
        }
        res = self.client.post(TOKEN_OBTAIN_URL, payload_obtain)
        refresh_token = res.data['refresh']

        payload_refresh = {
            'refresh': refresh_token,
        }
        refresh_one = self.client.post(TOKEN_REFRESH_URL, payload_refresh)
        refresh_two = self.client.post(TOKEN_REFRESH_URL, payload_refresh)

        self.assertEqual(refresh_two.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_bad_credentials(self):
        """Test returns error if refresh token is invalid"""
        payload_obtain = {
            'email': self.user.email,
            'password': 'testpass123',
        }
        res = self.client.post(TOKEN_OBTAIN_URL, payload_obtain)

        payload_refresh = {
            'refresh': 'invalid',
        }
        refresh = self.client.post(TOKEN_REFRESH_URL, payload_refresh)

        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_refresh_token_invalid(self):
        """Test returns error if refresh token is expired"""
        refresh_token = RefreshToken.for_user(self.user)
        refresh_token['exp'] = datetime.now() - timedelta(days=1)
        refresh_token_string = str(refresh_token)

        payload_refresh = {
            'refresh': refresh_token_string,
        }
        refresh = self.client.post(
            TOKEN_REFRESH_URL,
            json.dumps(payload_refresh),
            content_type='application/json'
        )
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)