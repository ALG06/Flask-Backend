from flask import Blueprint, jsonify, request
from datetime import datetime

donations_bp = Blueprint("donations", __name__)


@donations_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "Donations route"}), 200


@donations_bp.route("/create", methods=["POST"])
def create(supabase):
    """
    Para crear una Donation, se debe enviar un JSON con los siguientes campos:
    id: int
    date: date
    time: time
    state: string
    id_donor: int
    id_calendar: int
    id_point: int
    type: string
    pending: boolean
    """
    try:
        data = request.get_json()

        required_fields = ['id', 'date', 'time', 'state', 'id_donor',
                           'id_calendar', 'id_point', 'type', 'pending']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        response = supabase.table("donations").insert({
            "id": data['id'],
            "date": data['date'],
            "time": data['time'],
            "state": data['state'],
            "id_donor": data['id_donor'],
            "id_calendar": data['id_calendar'],
            "id_point": data['id_point'],
            "type": data['type'],
            "pending": data['pending'],
            "created_at": datetime.now(datetime.timezone.utc).isoformat()
        }).execute()

        return jsonify(response.data[0]), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/update", methods=["PUT"])
def update(supabase):
    """
    Para actualizar una Donation, se debe enviar un JSON con los siguientes campos:
    id: int
    date: date
    time: time
    state: string
    id_donor: int
    id_calendar: int
    id_point: int
    type: string
    pending: boolean
    """
    try:
        data = request.get_json()

        if 'id' not in data:
            return jsonify({'error': 'Missing donation ID'}), 400

        update_data = {}
        updateable_fields = ['date', 'time', 'state', 'id_donor',
                             'id_calendar', 'id_point', 'type', 'pending']

        for field in updateable_fields:
            if field in data:
                update_data[field] = data[field]

        update_data['updated_at'] = datetime.utcnow().isoformat()

        response = supabase.table("donations") \
            .update(update_data) \
            .eq('id', data['id']) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Donation not found'}), 404

        return jsonify(response.data[0]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/delete", methods=["DELETE"])
def delete(supabase):
    """
    Para eliminar una Donation, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    try:
        # Get data from request
        data = request.get_json()

        # Validate ID is present
        if 'id' not in data:
            return jsonify({'error': 'Missing donation ID'}), 400

        # Delete donation from Supabase
        response = supabase.table("donations") \
            .delete() \
            .eq('id', data['id']) \
            .execute()

        if not response.data:
            return jsonify({'error': 'Donation not found'}), 404

        return jsonify({'message': 'Donation deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/list", methods=["GET"])
def list(supabase):
    """
    Para listar todas las Donations, se debe enviar un JSON con el siguiente campo:
    id: int (opcional - si se proporciona, filtra por ID)
    """
    try:
        donation_id = request.args.get('id')

        query = supabase.table("donations").select("*")

        if donation_id:
            query = query.eq('id', donation_id)

        response = query.execute()

        if not response.data:
            return jsonify([]), 200

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/list_by_donor", methods=["GET"])
def list_by_donor(supabase):
    """
    Para listar todas las Donations de un Donor, se debe enviar un JSON con el siguiente campo:
    id_donor: int
    """
    try:
        donor_id = request.args.get('id_donor')

        if not donor_id:
            return jsonify({'error': 'Missing donor ID'}), 400

        response = supabase.table("donations") \
            .select(
            "*",
            count="exact"
        ) \
            .eq('id_donor', donor_id) \
            .order('date', desc=True) \
            .execute()

        if not response.data:
            return jsonify([]), 200

        return jsonify({
            'donations': response.data,
            'total_count': response.count if hasattr(response, 'count') else len(response.data)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@donations_bp.route("/pending", methods=["GET"])
def list_pending(supabase):
    """Lista de donaciones pendientes"""
    try:
        response = supabase.table("donations") \
            .select("*") \
            .eq('pending', True) \
            .order('date', desc=True) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/by_date_range", methods=["GET"])
def list_by_date_range(supabase):
    """Lista de donaciones por rango de fechas"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Missing date range parameters'}), 400

        response = supabase.table("donations") \
            .select("*") \
            .gte('date', start_date) \
            .lte('date', end_date) \
            .order('date', desc=True) \
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500