# auth.py
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
import requests
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity
)
from oauthlib.oauth2 import WebApplicationClient
import json
from datetime import timedelta
import os

auth_bp = Blueprint('auth', __name__)

# Google OAuth 2.0 settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'mydb')

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth_bp.route("/login/google")
def google_login():
    """Initiates the Google OAuth2 login flow"""
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Prepare the Google login URL
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return jsonify({"auth_url": request_uri})

@auth_bp.route("/login/google/callback")
def google_callback():
    """Handles the Google OAuth2 callback"""
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Get tokens from Google
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    
    # Get user info from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        google_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        name = userinfo_response.json()["name"]
        
        # Authenticate with Odoo
        odoo_auth_url = f"{ODOO_URL}/api/auth/google"
        odoo_payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'db': ODOO_DB,
                'google_id': google_id,
                'email': email,
                'name': name
            }
        }
        
        try:
            response = requests.post(odoo_auth_url, json=odoo_payload)
            result = response.json()
            
            if 'error' not in result.get('result', {}):
                user_id = result['result']['user_id']
                odoo_token = result['result']['token']
                
                # Create JWT tokens
                access_token = create_access_token(
                    identity=user_id,
                    additional_claims={'odoo_token': odoo_token}
                )
                refresh_token = create_refresh_token(identity=user_id)
                
                return jsonify({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_id': user_id,
                    'name': name,
                    'email': email
                }), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Google authentication failed'}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify access token"""
    current_user_id = get_jwt_identity()
    return jsonify({'valid': True, 'user_id': current_user_id}), 200

@auth_bp.route('/test', methods=['GET'])
@jwt_required()
def test_auth():
    """Test protected endpoint"""
    current_user_id = get_jwt_identity()
    return jsonify({'message': 'Protected endpoint', 'user_id': current_user_id}), 200