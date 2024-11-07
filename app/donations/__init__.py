from flask import Blueprint, jsonify, request

donations_bp = Blueprint("donations", __name__)


@donations_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "Donations route"}), 200

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


