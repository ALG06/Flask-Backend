from flask import Blueprint, jsonify, request

campaigns_bp = Blueprint("campaigns", __name__)


@campaigns_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "Campaign route"}), 200
