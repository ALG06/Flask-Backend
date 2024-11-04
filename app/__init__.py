from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from .sample import sample_bp

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes import auth_bp

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(sample_bp, url_prefix="/sample")

    return app
