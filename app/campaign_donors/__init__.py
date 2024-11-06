from flask import Blueprint, jsonify, request

campaign_donors_bp = Blueprint("campaign donors", __name__)


@campaign_donors_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "Campaign donors route"}), 200
