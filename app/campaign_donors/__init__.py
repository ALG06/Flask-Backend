from flask import Blueprint, jsonify, request
from datetime import datetime
from app.db import supabase


campaign_donors_bp = Blueprint("campaign_donors", __name__)


@campaign_donors_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "Campaign donors route"}), 200


@campaign_donors_bp.route("/create", methods=["POST"])
def create():
    """
    Para crear un Campaign Donor, se debe enviar un JSON con los siguientes campos:
    campaign_id: int
    donor_id: int
    """
    try:
        data = request.get_json()

        required_fields = ['campaign_id', 'donor_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        campaign = supabase.table("campaigns") \
            .select("*") \
            .eq('id', data['campaign_id']) \
            .single() \
            .execute()

        if not campaign.data:
            return jsonify({'error': 'Campaign not found'}), 404

        donor = supabase.table("donors") \
            .select("*") \
            .eq('id', data['donor_id']) \
            .single() \
            .execute()

        if not donor.data:
            return jsonify({'error': 'Donor not found'}), 404

        existing = supabase.table("campaign_donors") \
            .select("*") \
            .eq('campaign_id', data['campaign_id']) \
            .eq('donor_id', data['donor_id']) \
            .execute()

        if existing.data:
            return jsonify({'error': 'Donor is already registered in this campaign'}), 400

        response = supabase.table("campaign_donors").insert({
            "campaign_id": data['campaign_id'],
            "donor_id": data['donor_id'],
            "created_at": datetime.utcnow().date().isoformat()
        }).execute()

        return jsonify(response.data[0]), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaign_donors_bp.route("/delete", methods=["DELETE"])
def delete():
    """
    Para eliminar un Campaign Donor, se debe enviar un JSON con los siguientes campos:
    campaign_id: int
    donor_id: int
    """
    try:
        data = request.get_json()

        if 'campaign_id' not in data or 'donor_id' not in data:
            return jsonify({'error': 'Missing campaign_id or donor_id'}), 400

        response = supabase.table("campaign_donors") \
            .delete() \
            .eq('campaign_id', data['campaign_id']) \
            .eq('donor_id', data['donor_id']) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Campaign Donor association not found'}), 404

        return jsonify({'message': 'Campaign Donor association deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaign_donors_bp.route("/list", methods=["GET"])
def list():
    """
    Para listar todos los Campaign Donors, se debe enviar un JSON con los siguientes campos:
    campaign_id: int (optional)
    donor_id: int (optional)
    """
    try:
        campaign_id = request.args.get('campaign_id')
        donor_id = request.args.get('donor_id')

        query = supabase.table("campaign_donors").select("*")

        if campaign_id:
            query = query.eq('campaign_id', campaign_id)
        if donor_id:
            query = query.eq('donor_id', donor_id)

        response = query.execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaign_donors_bp.route("/list_by_campaign", methods=["GET"])
def list_by_campaign():
    """
    Para listar todos los Campaign Donors de una Campaign, se debe enviar un JSON con el siguiente campo:
    campaign_id: int
    """
    try:
        campaign_id = request.args.get('campaign_id')

        if not campaign_id:
            return jsonify({'error': 'Missing campaign_id'}), 400

        response = supabase.table("campaign_donors") \
            .select("*") \
            .eq('campaign_id', campaign_id) \
            .order('created_at', desc=True) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@campaign_donors_bp.route("/list_by_donor", methods=["GET"])
def list_by_donor():
    """
    Para listar todos los Campaign Donors de un Donor, se debe enviar un JSON con el siguiente campo:
    donor_id: int
    """
    try:
        donor_id = request.args.get('donor_id')

        if not donor_id:
            return jsonify({'error': 'Missing donor_id'}), 400

        response = supabase.table("campaign_donors") \
            .select("*") \
            .eq('donor_id', donor_id) \
            .order('created_at', desc=True) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500