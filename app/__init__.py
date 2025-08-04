from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import config
from prometheus_flask_exporter import PrometheusMetrics
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
metrics = PrometheusMetrics()  

def create_app():
    app = Flask(__name__)

    # Load DB config from environment
    db_params = config()
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '4f8b31dc8ee3437486e3424bcb2d6f0b'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']

    # Initialize Flask extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    from app import models
    from app.routes import register_routes
    register_routes(app)

    # Register Prometheus metrics route AFTER routes are set up
    metrics.init_app(app)

    # Create tables if they don’t exist
    with app.app_context():
        db.create_all()

    return app
