from flask import Blueprint, jsonify, request
from datetime import datetime
from app.db import supabase


donation_points_bp = Blueprint("donation_points", __name__)


@donation_points_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "Donation Points route"}), 200


@donation_points_bp.route("/create", methods=["POST"])
def create():
    """
    Para crear un Donation Point, se debe enviar un JSON con los siguientes campos:
    name: string
    address: text
    lat: float
    lon: float
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'address', 'lat', 'lon']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create donation point in Supabase
        response = supabase.table("donation_points").insert({
            "name": data['name'],
            "address": data['address'],
            "lat": data['lat'],
            "lon": data['lon'],
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify(response.data[0]), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donation_points_bp.route("/update/<int:point_id>", methods=["PUT"])
def update(point_id):
    """
    Para actualizar un Donation Point, se debe enviar un JSON con los campos a actualizar:
    name: string (optional)
    address: text (optional)
    lat: float (optional)
    lon: float (optional)
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create a dictionary with only the provided fields
        update_data = {}
        updatable_fields = ['name', 'address', 'lat', 'lon']

        for field in updatable_fields:
            if field in data:
                # Validate and convert lat/lon to float if provided
                if field in ['lat', 'lon']:
                    try:
                        update_data[field] = float(data[field])
                    except ValueError:
                        return jsonify({'error': f'Invalid format for {field}, must be a float'}), 400
                else:
                    update_data[field] = data[field]

        # Ensure there's something to update
        if not update_data:
            return jsonify({'error': 'No updatable fields provided'}), 400


        # Update the donation point in Supabase
        response = (supabase.table("donation_points")
            .update(update_data)
            .eq("id", point_id)
            .execute())

        # Check if the update was successful
        if not response.data or len(response.data) == 0:
            return jsonify({'error': f'Donation point not found'}), 404

        return jsonify({'message': 'Donation point updated successfully', 'data': response.data[0]}), 200

    except ValueError as ve:
        return jsonify({'error': f'Invalid data format: {str(ve)}'}), 400
    except Exception as e:
        # Add detailed logging for debugging
        print(f"Error updating donation point: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred while updating donation point'}), 500
@donation_points_bp.route("/delete/<int:point_id>", methods=["DELETE"])
def delete(point_id):
    """
    Para eliminar un Donation Point por su ID
    """
    try:
        response = supabase.table("donation_points") \
            .delete() \
            .eq('id', point_id) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Donation point not found'}), 404

        return jsonify({'message': 'Donation point deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donation_points_bp.route("/list", methods=["GET"])
def list():
    """
    Lista todos los Donation Points.
    Parámetros opcionales en URL:
    name: string (filter by name)
    """
    try:
        # Get query parameters
        name = request.args.get('name')

        # Start query
        query = supabase.table("donation_points").select("*")

        # Apply filters if provided
        if name:
            query = query.ilike('name', f'%{name}%')

        # Execute query
        response = query.order('created_at', desc=True).execute()

        return jsonify({
            'points': response.data,
            'total': len(response.data)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donation_points_bp.route("/<int:point_id>", methods=["GET"])
def get_by_id(point_id):
    """
    Obtiene un Donation Point por su ID
    """
    try:
        response = supabase.table("donation_points") \
            .select("*") \
            .eq('id', point_id) \
            .single() \
            .execute()

        if not response.data:
            return jsonify({'error': 'Donation point not found'}), 404

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


0