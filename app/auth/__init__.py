# app/auth/__init__.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    verify_jwt_in_request
)
from flask_jwt_extended.exceptions import InvalidHeaderError, NoAuthorizationError
from jwt.exceptions import InvalidTokenError
import requests
from oauthlib.oauth2 import WebApplicationClient
import json
from functools import wraps

auth_bp = Blueprint('auth', __name__)

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def get_google_client():
    """Get Google OAuth client instance"""
    return WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def jwt_required_with_invalid_handling(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except (InvalidHeaderError, NoAuthorizationError, InvalidTokenError):
            return jsonify({"msg": "Invalid or missing token"}), 401
    return wrapper

@auth_bp.route("/login/google")
def google_login():
    """Initiates the Google OAuth2 login flow"""
    client = get_google_client()
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return jsonify({"auth_url": request_uri})

@auth_bp.route("/login/google/callback")
def google_callback():
    """Handles the Google OAuth2 callback"""
    client = get_google_client()
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
        auth=(current_app.config['GOOGLE_CLIENT_ID'], 
              current_app.config['GOOGLE_CLIENT_SECRET']),
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
        
        # Create JWT tokens
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': google_id,
            'name': name,
            'email': email
        }), 200
            
    return jsonify({'error': 'Google authentication failed'}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify access token"""
    current_user = get_jwt_identity()
    return jsonify({'valid': True, 'user_id': current_user}), 200

@auth_bp.route('/test', methods=['GET'])
@jwt_required_with_invalid_handling
def test_auth():
    """Test protected endpoint"""
    current_user = get_jwt_identity()
    return jsonify({'message': 'Protected endpoint', 'user_id': current_user}), 200