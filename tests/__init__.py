# tests/__init__.py
import os
import sys
from flask_testing import TestCase
from app import create_app, db
from config import Config

# Configure paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Enable HTTP for OAuth testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

class BaseTestCase(TestCase):
    """Base Tests"""
    def create_app(self):
        """Create the app for testing"""
        app = create_app(TestConfig)
        return app

    def setUp(self):
        """Set up test environment"""
        db.create_all()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

# Mock responses for Google OAuth
MOCK_GOOGLE_PROVIDER_CONFIG = {
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth",
    "token_endpoint": "https://oauth2.googleapis.com/token",
    "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
}

MOCK_GOOGLE_TOKEN_RESPONSE = {
    "access_token": "mock_google_token",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "openid email profile",
    "id_token": "mock_id_token"
}

MOCK_GOOGLE_USERINFO = {
    "sub": "12345",
    "email": "test@example.com",
    "email_verified": True,
    "name": "Test User"
}

def create_test_headers(token):
    """Create authorization headers for testing"""
    return {'Authorization': f'Bearer {token}'}

def get_json_response(response):
    """Get JSON from response and decode it"""
    return response.json if hasattr(response, 'json') else response.get_json()