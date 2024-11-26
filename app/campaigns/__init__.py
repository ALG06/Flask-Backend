from flask import Blueprint, jsonify, request
from datetime import datetime
from app.db import supabase


campaigns_bp = Blueprint("campaigns", __name__)


@campaigns_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "Campaign route"}), 200


@campaigns_bp.route("/create", methods=["POST"])
def create():
    """
    Para crear una Campaign, se debe enviar un JSON con los siguientes campos:
    name: string
    start_date: date
    end_date: date
    """
    try:
        data = request.get_json()

        required_fields = ['name', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if data['start_date'] >= data['end_date']:
            return jsonify({'error': 'Start date must be before end date'}), 400

        response = supabase.table("campaigns").insert({
            "name": data['name'],
            "start_date": data['start_date'],
            "end_date": data['end_date'],
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }).execute()

        return jsonify(response.data[0]), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaigns_bp.route("/update", methods=["PUT"])
def update():
    """
    Para actualizar una Campaign, se debe enviar un JSON con los siguientes campos:
    id: int
    name: string (optional)
    start_date: date (optional)
    end_date: date (optional)
    active: boolean (optional)
    """
    try:
        data = request.get_json()

        if 'id' not in data:
            return jsonify({'error': 'Missing campaign ID'}), 400

        update_data = {}
        updateable_fields = ['name', 'start_date', 'end_date', 'active']

        for field in updateable_fields:
            if field in data:
                update_data[field] = data[field]

        if 'start_date' in update_data and 'end_date' in update_data:
            if update_data['start_date'] >= update_data['end_date']:
                return jsonify({'error': 'Start date must be before end date'}), 400

        update_data['updated_at'] = datetime.utcnow().isoformat()

        response = supabase.table("campaigns") \
            .update(update_data) \
            .eq('id', data['id']) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Campaign not found'}), 404

        return jsonify(response.data[0]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaigns_bp.route("/", methods=["DELETE"])
def delete():
    """
    Deactivate a Campaign. 
    To deactivate a campaign, provide its ID as a query parameter.

    Query Parameters:
    - id: int -> The ID of the campaign to deactivate.

    Returns:
    - 200: Success message if the campaign was deactivated.
    - 404: Error if the campaign was not found.
    - 400: Error if the ID parameter is missing.
    - 500: Error message in case of failure.
    """
    try:
        campaign_id = request.args.get('id')

        if not campaign_id:
            return jsonify({'error': 'Missing campaign ID'}), 400

        response = supabase.table("campaigns") \
            .update({"active": False}) \
            .eq('id', campaign_id) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Campaign not found'}), 404

        return jsonify({'message': 'Campaign deactivated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@campaigns_bp.route("/list", methods=["GET"])
def list():
    """
    Para listar todas las Campaigns, se debe enviar un JSON con el siguiente campo:
    id: int (opcional)
    active: boolean (opcional)
    """
    try:
        campaign_id = request.args.get('id')
        active = request.args.get('active')

        query = supabase.table("campaigns").select("*")

        if campaign_id:
            query = query.eq('id', campaign_id)
        if active is not None:
            query = query.eq('active', active.lower() == 'true')

        response = query.order('start_date', desc=True).execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaigns_bp.route("/list_by_donor/<int:donor_id>", methods=["GET"])
def list_by_donor(donor_id):
    """
    Para listar todas las Campaigns de un Donor por su ID
    URL: /campaigns/list_by_donor/1 (donde 1 es el id del donor)
    """
    try:
        if not donor_id:
            return jsonify({'error': 'Missing donor ID'}), 400

        response = supabase.table("campaigns") \
            .select(
            "campaigns.id",
            "campaigns.name",
            "campaigns.start_date",
            "campaigns.end_date"        ) \
            .join("donations", "campaigns.id", "eq", "donations.id_campaign") \
            .eq("donations.id_donor", donor_id) \
            .order('campaigns.start_date', desc=True) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@campaigns_bp.route("/active", methods=["GET"])
def list_active():
    """Lista de campañas activas"""
    try:
        current_date = datetime.utcnow().date().isoformat()

        response = supabase.table("campaigns") \
            .select("*") \
            .eq('active', True) \
            .order('start_date', desc=True) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaigns_bp.route("/upcoming", methods=["GET"])
def list_upcoming():
    """Lista de campañas próximas"""
    try:
        current_date = datetime.utcnow().date().isoformat()

        response = supabase.table("campaigns") \
            .select("*") \
            .eq('active', True) \
            .gt('start_date', current_date) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


