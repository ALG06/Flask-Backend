from flask import Blueprint, jsonify, request

donations_bp = Blueprint("donations", __name__)


@donations_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "Donations route"}), 200
