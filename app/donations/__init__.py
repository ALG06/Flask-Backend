from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from app.db import supabase
import qrcode  
import io  
import base64  

donations_bp = Blueprint("donations", __name__)

@donations_bp.route("", methods=["GET"])
def sample():
    return jsonify({"message": "Donations route"}), 200

@donations_bp.route("/create", methods=["POST"])
def create():
    try:
        # Parse JSON data
        data = request.get_json()

        # Validate required fields for the donation
        required_fields = ['id', 'date', 'time', 'state', 'id_donor', 'id_point', 'type', 'pending', 'foods']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Insert donation into Supabase
        response = supabase.table("donations").insert({
            "id": data['id'],
            "date": data['date'],
            "time": data['time'],
            "state": data['state'],
            "id_donor": data['id_donor'],
            "id_point": data['id_point'],
            "type": data['type'],
            "pending": data['pending'],
        }).execute()

        # Check if the insert was successful
        if not response.data or len(response.data) == 0:
            return jsonify({'error': 'Failed to create donation'}), 500

        # Get the newly created donation ID
        donation_id = response.data[0]['id']

        # Prepare food entries for bulk insert
        food_data_list = [
            {
                "id_donation": donation_id,
                "name": food["name"],
                "quantity": food["quantity"],
                "category": food["category"],
                "perishable": food["perishable"],
            }
            for food in data['foods']
        ]

        # Insert food items into Supabase
        food_response = supabase.table("food").insert(food_data_list).execute()

        # Check if food items were successfully inserted
        if not food_response.data:
            return jsonify({'error': 'Failed to insert food items'}), 500

        # Generate QR Code for the donation ID
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(donation_id)
        qr.make(fit=True)

        # Save QR Code as binary data
        img = qr.make_image(fill='black', back_color='white')
        byte_io = io.BytesIO()
        img.save(byte_io, 'PNG')
        byte_io.seek(0)
        qr_image_data = byte_io.read()
        qr_image_data_base64 = base64.b64encode(qr_image_data).decode('utf-8')

        # Update donation with QR code
        qr_response = supabase.table("donations").update({
            "qr": qr_image_data_base64
        }).eq("id", donation_id).execute()

        # Check if the QR code was successfully updated
        if not qr_response.data:
            return jsonify({'error': 'Failed to update donation with QR code'}), 500

        return jsonify({"donation_id": donation_id, "qr_code": qr_image_data_base64}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/update", methods=["PUT"])
def update():
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
def delete():
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
def list():
    """
    Para listar todas las Donations, se debe enviar un JSON con los siguientes campos:
    id: int (opcional - si se proporciona, filtra por ID)
    details: bool (opcional - si se proporciona, obtiene más detalles)
    """
    try:
        donation_id = request.args.get('id')
        details = request.args.get('details', 'false').lower() == 'true'

        query = supabase.table("donations").select("*")

        if donation_id:
            query = query.eq('id', donation_id)

        response = query.execute()

        if not response.data:
            return jsonify([]), 200

        donations = response.data

        if details:
            for donation in donations:
                # Get all food items associated with this donation
                food_response = supabase.table("food") \
                    .select("*") \
                    .eq('id_donation', donation['id']) \
                    .execute()

                # Get donor information
                donor_response = supabase.table("donors") \
                    .select("name, phone, email") \
                    .eq('id', donation['id_donor']) \
                    .execute()

                donation['food_items'] = food_response.data
                donation['donor'] = donor_response.data
                donation['total_food_items'] = len(food_response.data)

        return jsonify(donations), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@donations_bp.route("/list_by_donor", methods=["GET"])
def list_by_donor():
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
def list_pending():
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
def list_by_date_range():
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


@donations_bp.route("/details/<int:donation_id>", defaults={'pending_status': None}, methods=["GET"])
@donations_bp.route("/details/<int:donation_id>/<pending_status>", methods=["GET"])
def get_donation_details(donation_id, pending_status):
    """
    Get donation details and associated food items by donation ID and optional pending status
    """
    try:
        query = supabase.table("donations").select("*").eq('id', donation_id)

        # Apply pending status filter if provided
        if pending_status is not None:
            pending = pending_status.lower() == 'true'
            query = query.eq('pending', pending)

        donation_response = query.single().execute()

        if not donation_response.data:
            return jsonify({'error': 'Donation not found'}), 404

        donation = donation_response.data

        # Get all food items associated with this donation
        food_response = supabase.table("food") \
            .select("*") \
            .eq('id_donation', donation_id) \
            .execute()
        
        donor_response = supabase.table("donors") \
            .select("name, phone, email") \
            .eq('id', donation['id_donor']) \
            .execute()
        
        response_data = {
            'donation': donation,
            'food_items': food_response.data,
            'donor': donor_response.data,
            'total_food_items': len(food_response.data)
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@donations_bp.route("/qrcode/<int:donation_id>", methods=["GET"])
def get_qr_code(donation_id):  # Add donation_id parameter here
    """
    Get donation qr code by ID
    """

    try:
        # No need to get from request.view_args since it's now a parameter
        print("hello")
        donation_response = supabase.table("donations") \
            .select("*") \
            .eq('id', donation_id) \
            .eq('pending', True) \
            .single() \
            .execute()
        print(donation_response)

        if not donation_response.data:
            return jsonify({'error': 'Donation not found or is expired'}), 404

        qr_code = donation_response.data.get("qr")
        if not qr_code:
            return jsonify({'error': 'QR code not available for this donation'}), 404

        # Return the QR code
        return jsonify({
            'qr': qr_code,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500