from flask import Blueprint, jsonify, request

donors_bp = Blueprint("donors", __name__)


@donors_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "donor route"}), 200
