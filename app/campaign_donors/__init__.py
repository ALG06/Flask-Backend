from flask import Blueprint, jsonify, request

campaign_donors_bp = Blueprint("campaign donors", __name__)

# TODO: Add proper CRUD functionality

@campaign_donors_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "Campaign donors route"}), 200



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




