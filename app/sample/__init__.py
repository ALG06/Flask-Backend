from flask import Blueprint, jsonify, request

sample_bp = Blueprint("sample", __name__)


@sample_bp.route("", methods=["GET"]) # /sample
def sample():
    return jsonify({"message": "Sample route"}), 200
