from flask import Blueprint, jsonify, request
from datetime import datetime

donors_bp = Blueprint("donors", __name__)


@donors_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "donor route"}), 200


@donors_bp.route("/create", methods=["POST"])
def create(supabase):
    """
    Para crear un Donor, se debe enviar un JSON con los siguientes campos:
    id: int
    name: string
    email: string
    phone: string
    """
    try:
        data = request.get_json()

        required_fields = ['id', 'name', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        response = supabase.table("donors").insert({
            "id": data['id'],
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return jsonify(response.data[0]), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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