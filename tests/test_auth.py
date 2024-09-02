import unittest
from unittest.mock import patch, MagicMock
import json
from app import create_app, db
from flask_jwt_extended import create_access_token, create_refresh_token
from config import Config
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Add this line

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    GOOGLE_CLIENT_ID = 'test-client-id'
    GOOGLE_CLIENT_SECRET = 'test-client-secret'
    WTF_CSRF_ENABLED = False
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    PROPAGATE_EXCEPTIONS = True
    OAUTHLIB_INSECURE_TRANSPORT = True  # Add this line

class TestAuth(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = create_app(TestConfig)
        
        # Add this line to allow OAuth2 over HTTP in testing
        self.app.config['OAUTHLIB_INSECURE_TRANSPORT'] = True
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all database tables
        db.create_all()
        
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
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_hello_world(self):
        """Test the root endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Hello, World!')

    @patch('requests.get')
    def test_google_login(self, mock_get):
        """Test initiating Google login."""
        # Mock Google discovery document
        mock_get.return_value.json.return_value = {
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth"
        }
        
        response = self.client.get('/auth/login/google')
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_url', json.loads(response.data))

    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback(self, mock_get, mock_post):
        """Test Google OAuth callback."""
        # Mock Google provider configuration
        mock_provider_config = {
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth",
            "token_endpoint": "https://oauth2.googleapis.com/token",
            "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
        }
        
        # Mock Google token response
        mock_token_response = {
            "access_token": "mock_google_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "openid email profile",
            "id_token": "mock_id_token"  # Add this line
        }

        # Set up the sequence of mock responses
        mock_get.side_effect = [
            MagicMock(json=lambda: mock_provider_config),  # For provider config
            MagicMock(json=lambda: self.mock_google_user_info)  # For user info
        ]
        
        mock_post.return_value = MagicMock(
            json=lambda: mock_token_response,
            status_code=200
        )
        
        with self.app.test_request_context():
            response = self.client.get(
                '/auth/login/google/callback?code=mock_code&state=mock_state'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('access_token', data)
            self.assertIn('refresh_token', data)
            self.assertIn('user_id', data)

    def test_protected_endpoint(self):
        """Test accessing protected endpoint."""
        with self.app.test_request_context():
            access_token = create_access_token('test_user')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = self.client.get('/auth/test', headers=headers)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('message', data)
            self.assertIn('user_id', data)

    def test_verify_token(self):
        """Test token verification."""
        with self.app.test_request_context():
            access_token = create_access_token('test_user')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = self.client.get('/auth/verify', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(json.loads(response.data)['valid'])

    def test_refresh_token(self):
        """Test token refresh."""
        with self.app.test_request_context():
            refresh_token = create_refresh_token('test_user')
            headers = {'Authorization': f'Bearer {refresh_token}'}
            
            response = self.client.post('/auth/refresh', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIn('access_token', json.loads(response.data))

    def test_protected_endpoint_no_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/auth/test')
        self.assertEqual(response.status_code, 401)

    def test_invalid_token(self):
        """Test using invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = self.client.get('/auth/test', headers=headers)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()