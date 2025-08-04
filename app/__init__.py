from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import config
from prometheus_flask_exporter import PrometheusMetrics
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
metrics = PrometheusMetrics.for_app_factory()  # <-- key for factory use

def create_app():
    app = Flask(__name__)

    db_params = config()
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '4f8b31dc8ee3437486e3424bcb2d6f0b'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    metrics.init_app(app)

    from app import models
    from app.routes import register_routes
    register_routes(app)  # Clean import

    with app.app_context():
        db.create_all()

    return app
