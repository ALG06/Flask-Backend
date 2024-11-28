from flask import Blueprint
from .donors import donors_bp
from .donations import donations_bp
from .campaigns import campaigns_bp
from .campaign_donors import campaign_donors_bp
from .donation_points import donation_points_bp
from .auth import auth_bp


donors_bp = Blueprint("donors", donors_bp)
auth_bp = Blueprint("auth", auth_bp)
donations_bp = Blueprint("donations", donations_bp)
campaigns_bp = Blueprint("campaigns", campaigns_bp) 
campaign_donors_bp = Blueprint("campaign donors", campaign_donors_bp)
donation_points_bp = Blueprint("donation_points", donation_points_bp)
