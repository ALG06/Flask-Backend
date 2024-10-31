import unittest
import json
from flask import current_app
from app import create_app, db
from app.models import User
from config import TestConfig

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        test_user = User(
            email='test@example.com',
            username='testuser'
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_success(self):
        response = self.client.post('/api/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'test123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', json.loads(response.data))
        self.assertIn('refresh_token', json.loads(response.data))

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)

    def test_protected_route(self):
        # First login to get token
        login_response = self.client.post('/api/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'test123'
            }),
            content_type='application/json'
        )
        
        token = json.loads(login_response.data)['access_token']
        
        # Test with valid token
        response = self.client.get('/api/protected',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Test without token
        response = self.client.get('/api/protected')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()