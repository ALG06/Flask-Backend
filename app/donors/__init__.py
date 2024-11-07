from flask import Blueprint, jsonify, request

donors_bp = Blueprint("donors", __name__)


@donors_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "donor route"}), 200


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

