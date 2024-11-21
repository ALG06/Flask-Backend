from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from .sample import sample_bp
from .donors import donors_bp
from .donations import donations_bp
from .campaigns import campaigns_bp
from .campaign_donors import campaign_donors_bp
from .auth import auth_bp
from .db import db

jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    @app.route("/")
    def hello_world():
        return "Hello, World! \n This is the backend point of Punto Donativo. \n Please, use the API to interact with the database."

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(sample_bp, url_prefix="/sample")
    app.register_blueprint(donors_bp, url_prefix="/donors")
    app.register_blueprint(donations_bp, url_prefix="/donations")
    app.register_blueprint(campaigns_bp, url_prefix="/campaigns")
    app.register_blueprint(campaign_donors_bp, url_prefix="/campaign_donors")

    return app
