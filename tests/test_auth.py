import unittest
from unittest.mock import patch, MagicMock
import json
from flask import url_for
from app import create_app  # Import your Flask app factory
from flask_jwt_extended import create_access_token, create_refresh_token

class TestAuth(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock Google OAuth response
        self.mock_google_user_info = {
            "sub": "12345",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User"
        }
        
        # Mock Odoo response
        self.mock_odoo_response = {
            "result": {
                "user_id": 1,
                "token": "mock_odoo_token",
                "name": "Test User",
                "email": "test@example.com"
            }
        }

    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop()

    @patch('requests.get')
    def test_google_login(self, mock_get):
        """Test initiating Google login."""
        # Mock Google discovery document
        mock_get.return_value.json.return_value = {
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth"
        }
        
        response = self.client.get('/auth/login/google')
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_url', response.json)

    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback(self, mock_get, mock_post):
        """Test Google OAuth callback."""
        # Mock Google token response
        mock_post.return_value.json.return_value = {
            "access_token": "mock_google_token"
        }
        
        # Mock Google user info response
        mock_get.return_value.json.return_value = self.mock_google_user_info
        
        # Mock Odoo authentication response
        mock_post.return_value.json.return_value = self.mock_odoo_response
        
        response = self.client.get(
            '/auth/login/google/callback?code=mock_code'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user_id', data)

    def test_protected_endpoint(self):
        """Test accessing protected endpoint."""
        # Create a test access token
        access_token = create_access_token('test_user')
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = self.client.get(
            '/auth/test',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertIn('user_id', response.json)

    def test_verify_token(self):
        """Test token verification."""
        access_token = create_access_token('test_user')
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = self.client.get(
            '/auth/verify',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['valid'])

    def test_refresh_token(self):
        """Test token refresh."""
        refresh_token = create_refresh_token('test_user')
        headers = {'Authorization': f'Bearer {refresh_token}'}
        
        response = self.client.post(
            '/auth/refresh',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_protected_endpoint_no_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/auth/test')
        self.assertEqual(response.status_code, 401)

    def test_invalid_token(self):
        """Test using invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = self.client.get(
            '/auth/test',
            headers=headers
        )
        self.assertEqual(response.status_code, 401)

    @patch('requests.post')
    def test_google_callback_unverified_email(self, mock_post):
        """Test Google callback with unverified email."""
        unverified_user = self.mock_google_user_info.copy()
        unverified_user['email_verified'] = False
        
        mock_post.return_value.json.return_value = {"userinfo": unverified_user}
        
        response = self.client.get(
            '/auth/login/google/callback?code=mock_code'
        )
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.json)

if __name__ == '__main__':
    unittest.main()