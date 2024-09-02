from datetime import timedelta
from unittest.mock import patch, MagicMock
import json
import os
from dotenv import load_dotenv
from tests import (
    BaseTestCase, 
    create_test_headers,
    get_json_response,
    MOCK_GOOGLE_PROVIDER_CONFIG,
    MOCK_GOOGLE_TOKEN_RESPONSE,
    MOCK_GOOGLE_USERINFO
)
from flask_jwt_extended import create_access_token, create_refresh_token

# Load environment variables from .env file
load_dotenv()

class TestAuth(BaseTestCase):
    """Test auth blueprint."""

    def test_hello_world(self):
        """Test the root endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Hello, World!')

    @patch('requests.get')
    def test_google_login(self, mock_get):
        """Test initiating Google login."""
        mock_get.return_value.json.return_value = MOCK_GOOGLE_PROVIDER_CONFIG
        
        response = self.client.get('/auth/login/google')
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_url', get_json_response(response))

    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback(self, mock_get, mock_post):
        """Test Google OAuth callback."""
        # Set up mock responses
        mock_get.side_effect = [
            MagicMock(json=lambda: MOCK_GOOGLE_PROVIDER_CONFIG),
            MagicMock(json=lambda: MOCK_GOOGLE_USERINFO)
        ]
        
        mock_post.return_value = MagicMock(
            json=lambda: MOCK_GOOGLE_TOKEN_RESPONSE,
            status_code=200
        )
        
        response = self.client.get('/auth/login/google/callback?code=mock_code&state=mock_state')
        self.assertEqual(response.status_code, 200)
        data = get_json_response(response)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user_id', data)

    def test_protected_endpoint(self):
        """Test accessing protected endpoint."""
        with self.app.test_request_context():
            access_token = create_access_token('test_user')
            response = self.client.get(
                '/auth/test',
                headers=create_test_headers(access_token)
            )
            self.assertEqual(response.status_code, 200)
            data = get_json_response(response)
            self.assertIn('message', data)
            self.assertIn('user_id', data)

    def test_verify_token(self):
        """Test token verification."""
        with self.app.test_request_context():
            access_token = create_access_token('test_user')
            response = self.client.get(
                '/auth/verify',
                headers=create_test_headers(access_token)
            )
            self.assertEqual(response.status_code, 200)
            data = get_json_response(response)
            self.assertTrue(data['valid'])
            self.assertEqual(data['user_id'], 'test_user')

    def test_refresh_token(self):
        """Test token refresh."""
        with self.app.test_request_context():
            refresh_token = create_refresh_token('test_user')
            response = self.client.post(
                '/auth/refresh',
                headers=create_test_headers(refresh_token)
            )
            self.assertEqual(response.status_code, 200)
            data = get_json_response(response)
            self.assertIn('access_token', data)

    def test_protected_endpoint_no_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/auth/test')
        self.assertEqual(response.status_code, 401)
        data = get_json_response(response)
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Invalid or missing token')

    def test_invalid_token(self):
        """Test using invalid token."""
        response = self.client.get(
            '/auth/test',
            headers=create_test_headers('invalid_token')
        )
        self.assertEqual(response.status_code, 401)
        data = get_json_response(response)
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Invalid or missing token')

    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback_unverified_email(self, mock_get, mock_post):
        """Test Google callback with unverified email."""
        # Mock responses with unverified email
        unverified_user_info = MOCK_GOOGLE_USERINFO.copy()
        unverified_user_info['email_verified'] = False
        
        mock_get.side_effect = [
            MagicMock(json=lambda: MOCK_GOOGLE_PROVIDER_CONFIG),
            MagicMock(json=lambda: unverified_user_info)
        ]
        
        mock_post.return_value = MagicMock(
            json=lambda: MOCK_GOOGLE_TOKEN_RESPONSE,
            status_code=200
        )
        
        response = self.client.get('/auth/login/google/callback?code=mock_code&state=mock_state')
        self.assertEqual(response.status_code, 401)
        data = get_json_response(response)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Google authentication failed')

    @patch('requests.get')
    def test_google_provider_cfg_failure(self, mock_get):
        """Test failure to get Google provider configuration."""
        mock_get.side_effect = Exception('Failed to get provider config')
        
        response = self.client.get('/auth/login/google')
        self.assertEqual(response.status_code, 500)
        data = get_json_response(response)
        self.assertIn('error', data)

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        with self.app.test_request_context():
            # Create a token that expires immediately
            access_token = create_access_token(
                'test_user',
                expires_delta=timedelta(seconds=-1)  # Already expired
            )
            response = self.client.get(
                '/auth/verify',
                headers=create_test_headers(access_token)
            )
            self.assertEqual(response.status_code, 401)
            data = get_json_response(response)
            self.assertIn('msg', data)
            self.assertIn('Token has expired', data['msg'])

    def test_refresh_with_access_token(self):
        """Test refresh endpoint with access token instead of refresh token."""
        with self.app.test_request_context():
            # Create an access token but try to use it as refresh token
            access_token = create_access_token('test_user')
            response = self.client.post(
                '/auth/refresh',
                headers=create_test_headers(access_token)
            )
            # JWT returns 422 for invalid token type
            self.assertEqual(response.status_code, 422)
            data = get_json_response(response)
            self.assertIn('msg', data)
            self.assertIn('Only refresh tokens are allowed', data['msg'])


if __name__ == '__main__':
    import unittest
    unittest.main()