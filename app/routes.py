from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from jinja2.filters import do_attr

from .donors import donors_bp
from .donations import donations_bp
from .campaigns import campaigns_bp
from .campaign_donors import campaign_donors_bp
from app.models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return (
            jsonify({"access_token": access_token, "refresh_token": refresh_token}),
            200,
        )

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({"message": f"Protected data for user {current_user_id}"}), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": access_token}), 200

@donors_bp.route("/create", methods=["POST"])
def create():
    """
    Para crear un Donor, se debe enviar un JSON con los siguientes campos:
    id: int
    name: string
    email: string
    phone: string
    """
    pass

@donors_bp.route("/update", methods=["PUT"])
def update():
    """
    Para actualizar un Donor, se debe enviar un JSON con los siguientes campos:
    id: int
    name: string
    email: string
    phone: string
    """
    pass

@donors_bp.route("/delete", methods=["DELETE"])
def delete():
    """
    Para eliminar un Donor, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass


# /donors/list  para hacerlo por ids
@donors_bp.route("/list", methods=["GET"])
def list():
    """
    Para listar todos los Donors, se debe enviar un JSON con el siguiente campo:
    id: int

    """
    pass


#Donations
@donations_bp.route("/create", methods=["POST"])
def create():
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
    pass

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
    pass

@donations_bp.route("/delete", methods=["DELETE"])
def delete():
    """
    Para eliminar una Donation, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass

@donations_bp.route("/list", methods=["GET"])
def list():
    """
    Para listar todas las Donations, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass

@donations_bp.route("/list_by_donor", methods=["GET"])
def list_by_donor():
    """
    Para listar todas las Donations de un Donor, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass


#Campaigns
@campaigns_bp.route("/create", methods=["POST"])
def create():
    """
    Para crear una Campaign, se debe enviar un JSON con los siguientes campos:
    name: string
    start_date: date
    end_date: date
    """
    pass

@campaigns_bp.route("/update", methods=["PUT"])
def update():
    """
    Para actualizar una Campaign, se debe enviar un JSON con los siguientes campos:
    name: string
    start_date: date
    end_date: date
    """
    pass

@campaigns_bp.route("/delete", methods=["DELETE"])
def delete():
    """
    Para eliminar una Campaign, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass

@campaigns_bp.route("/list", methods=["GET"])
def list():
    """
    Para listar todas las Campaigns, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass

@campaigns_bp.route("/list_by_donor", methods=["GET"])
def list_by_donor():
    """
    Para listar todas las Campaigns de un Donor, se debe enviar un JSON con el siguiente campo:
    id: int
    """
    pass


#Campaign Donors

@campaign_donors_bp.route("/create", methods=["POST"])
def create():
    """
    Para crear un Campaign Donor, se debe enviar un JSON con los siguientes campos:
    campaign_id: int
    donor_id: int
    """
    pass

@campaign_donors_bp.route("/update", methods=["PUT"])
def update():
    """
    Para actualizar un Campaign Donor, se debe enviar un JSON con los siguientes campos:
    campaign_id: int
    donor_id: int
    """
    pass

@campaign_donors_bp.route("/delete", methods=["DELETE"])
def delete():
    """
    Para eliminar un Campaign Donor, se debe enviar un JSON con los siguientes campos:
    campaign_id: int
    donor_id: int
    """
    pass

@campaign_donors_bp.route("/list", methods=["GET"])
def list():
    """
    Para listar todos los Campaign Donors, se debe enviar un JSON con los siguientes campos:
    campaign_id: int
    donor_id: int
    """
    pass

@campaign_donors_bp.route("/list_by_campaign", methods=["GET"])
def list_by_campaign():
    """
    Para listar todos los Campaign Donors de una Campaign, se debe enviar un JSON con el siguiente campo:
    campaign_id: int
    """
    pass

@campaign_donors_bp.route("/list_by_donor", methods=["GET"])
def list_by_donor():
    """
    Para listar todos los Campaign Donors de un Donor, se debe enviar un JSON con el siguiente campo:
    donor_id: int
    """
    pass









