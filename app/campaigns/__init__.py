from flask import Blueprint, jsonify, request

campaigns_bp = Blueprint("campaigns", __name__)


@campaigns_bp.route("", methods=["GET"]) # /sample
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





