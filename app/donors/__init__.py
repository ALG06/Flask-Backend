from flask import Blueprint, jsonify, request
from datetime import datetime
import bcrypt
import re
import jwt
import os


donors_bp = Blueprint("donors", __name__)


@donors_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "donor route"}), 200


@donors_bp.route("/create", methods=["POST"])
def create(supabase):
    """
    Para crear un Donor, se debe enviar un JSON con los siguientes campos:
    name: string
    email: string
    phone: string
    password: string
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if email already exists
        existing_user = supabase.table("donors") \
            .select("*") \
            .eq("email", data['email']) \
            .execute()

        if existing_user.data:
            return jsonify({'error': 'Email already registered'}), 400

        # Validate password length (minimum 6 characters)
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), salt)

        # Create donor in Supabase
        response = supabase.table("donors").insert({
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": hashed_password.decode('utf-8'),  # Store hashed password
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # Remove password from response
        donor_data = response.data[0]
        if 'password' in donor_data:
            del donor_data['password']

        return jsonify(donor_data), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donors_bp.route("/login", methods=["POST"])
def login(supabase):
    """
    Para iniciar sesión, se debe enviar un JSON con los siguientes campos:
    email: string
    password: string
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get donor by email
        response = supabase.table("donors") \
            .select("*") \
            .eq("email", data['email']) \
            .single() \
            .execute()

        if not response.data:
            return jsonify({'error': 'Invalid email or password'}), 401

        donor = response.data

        # Verify password
        if not bcrypt.checkpw(data['password'].encode('utf-8'),
                              donor['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Remove password from donor object
        if 'password' in donor:
            del donor['password']

        return jsonify({
            'message': 'Login successful',
            'donor': donor
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Simple function to check if user exists and password matches
def verify_donor_credentials(supabase, email, password):
    try:
        response = supabase.table("donors") \
            .select("*") \
            .eq("email", email) \
            .single() \
            .execute()

        if not response.data:
            return None

        donor = response.data

        if bcrypt.checkpw(password.encode('utf-8'),
                          donor['password'].encode('utf-8')):
            del donor['password']
            return donor

        return None
    except:
        return None




@donors_bp.route("/update", methods=["PUT"])
def update(supabase):
    """
    Para actualizar un Donor, se debe enviar un JSON con los siguientes campos:
    id: int
    name: string
    email: string
    phone: string
    """
    try:
        data = request.get_json()

        if 'id' not in data:
            return jsonify({'error': 'Missing donor ID'}), 400

        # Create update dict with only provided fields
        update_data = {}
        for field in ['name', 'email', 'phone']:
            if field in data:
                update_data[field] = data[field]

        update_data['updated_at'] = datetime.utcnow().isoformat()

        response = supabase.table("donors") \
            .update(update_data) \
            .eq('id', data['id']) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Donor not found'}), 404

        return jsonify(response.data[0]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donors_bp.route("/delete", methods=["DELETE"])
def delete(supabase):
    """
    Para eliminar un Donor, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    try:
        data = request.get_json()

        if 'id' not in data:
            return jsonify({'error': 'Missing donor ID'}), 400

        response = supabase.table("donors") \
            .delete() \
            .eq('id', data['id']) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Donor not found'}), 404

        return jsonify({'message': 'Donor deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donors_bp.route("/list", methods=["GET"])
def list(supabase):
    """
    Para listar todos los Donors, se debe enviar un JSON con el siguiente campo:
    id: int (opcional - si se proporciona, filtra por ID)
    """
    try:
        donor_id = request.args.get('id')

        query = supabase.table("donors").select("*")

        if donor_id:
            query = query.eq('id', donor_id)

        response = query.execute()

        if not response.data:
            return jsonify([]), 200

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donors_bp.route("/list_campaigns", methods=["GET"])
def list_campaigns(supabase):
    # Get current date in ISO format
    current_date = datetime.utcnow().date().isoformat()

    response = supabase.table("campaigns") \
        .select("*") \
        .gte("start_date", current_date) \
        .execute()

    campaigns = response.data
    return jsonify(campaigns), 200


@donors_bp.route("/past_campaigns", methods=["GET"])
def past_campaigns(supabase):
    current_date = datetime.utcnow().date().isoformat()

    response = supabase.table("campaigns") \
        .select("*") \
        .lt("end_date", current_date) \
        .order("start_date", desc=True) \
        .execute()

    campaigns = response.data
    return jsonify(campaigns), 200