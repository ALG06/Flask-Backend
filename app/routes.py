from flask import Blueprint, jsonify, request

from jinja2.filters import do_attr

from .donors import donors_bp
from .donations import donations_bp
from .campaigns import campaigns_bp
from .campaign_donors import campaign_donors_bp
from .auth import auth_bp


donors_bp = Blueprint("donors", __name__)
auth_bp = Blueprint("auth", __name__)
donations_bp = Blueprint("donations", __name__)
campaigns_bp = Blueprint("campaigns", __name__)
campaign_donors_bp = Blueprint("campaign donors", __name__)

