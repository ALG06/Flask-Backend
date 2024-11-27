from flask import Blueprint, jsonify, request
from datetime import datetime
import bcrypt
import re
from app.db import supabase
import hashlib



donors_bp = Blueprint("donors", __name__)


@donors_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "donor route"}), 200


@donors_bp.route("/create", methods=["POST"])
def create():
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

        # Hash the password with SHA-256
        hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()

        # Create donor in Supabase
        response = supabase.table("donors").insert({
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": hashed_password,
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
def login():
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

        # Hash the input password and compare
        hashed_input_password = hashlib.sha256(data['password'].encode()).hexdigest()

        if hashed_input_password != donor['password']:
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
@donors_bp.route("/update", methods=["PUT"])
def update():
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
def delete():
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
def list():
    """
    Lista todos los donors. Parámetros opcionales:
    id: int (filter by ID)
    name: string (filter by name)
    email: string (filter by email)
    order: string (order by field, default: 'created_at')
    order_direction: string ('asc' or 'desc', default: 'desc')
    """
    try:
        # Get query parameters
        donor_id = request.args.get('id')
        name = request.args.get('name')
        email = request.args.get('email')
        order_by = request.args.get('order', 'created_at')
        order_direction = request.args.get('order_direction', 'desc')

        # Start query selecting specific fields (excluding password)
        query = supabase.table("donors").select(
            "id",
            "name",
            "email",
            "phone",
            "created_at"
        )

        # Apply filters if provide
        if donor_id:
            query = query.eq('id', donor_id)
        if name:
            query = query.ilike('name', f'%{name}%')
        if email:
            query = query.ilike('email', f'%{email}%')

        # Apply ordering
        query = query.order(order_by, desc=(order_direction.lower() == 'desc'))

        # Execute query
        response = query.execute()

        # Return empty list if no donors found
        if not response.data:
            return jsonify([]), 200

        return jsonify({
            'donors': response.data,
            'total': len(response.data)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@donors_bp.route("/list_campaigns", methods=["GET"])
def list_campaigns():
    # Get current date in ISO format
    current_date = datetime.utcnow().date().isoformat()

    response = supabase.table("campaigns") \
        .select("*") \
        .gte("start_date", current_date) \
        .execute()

    campaigns = response.data
    return jsonify(campaigns), 200


@donors_bp.route("/past_campaigns", methods=["GET"])
def past_campaigns():
    current_date = datetime.utcnow().date().isoformat()

    response = supabase.table("campaigns") \
        .select("*") \
        .lt("end_date", current_date) \
        .order("start_date", desc=True) \
        .execute()

    campaigns = response.data
    return jsonify(campaigns), 200


@donors_bp.route("/stats/<int:donor_id>", methods=["GET"])
def get_donor_counts(donor_id):
    """
    Get count of donations, campaigns, and total food quantity (in KG) for a donor
    """
    try:
        # Get donations count
        donations_count = supabase.table("donations") \
            .select("*", count="exact") \
            .eq('id_donor', donor_id) \
            .execute()

        # Get campaigns count from campaign_donors table
        campaigns_count = supabase.table("campaign_donors") \
            .select("*", count="exact") \
            .eq('donor_id', donor_id) \
            .execute()

        # Get all food entries for donor's donations and sum their quantities
        donations = supabase.table("donations") \
            .select("id") \
            .eq('id_donor', donor_id) \
            .execute()

        total_kg = 0
        if donations.data:
            donation_ids = [d['id'] for d in donations.data]

            food_quantities = supabase.table("food") \
                .select("quantity") \
                .in_("id_donation", donation_ids) \
                .execute()

            # Sum quantities and convert to KG (divide by 100)
            total_kg = sum([item['quantity'] for item in food_quantities.data]) / 100

        return jsonify({
            'donor_id': donor_id,
            'total_donations': donations_count.count,
            'total_campaigns': campaigns_count.count,
            'total_kg_donated': round(total_kg, 2)  # Round to 2 decimal places
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500