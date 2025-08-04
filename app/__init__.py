from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

# Create Flask app
app = Flask(__name__)

# Load DB config
db_params = config()
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '4f8b31dc8ee3437486e3424bcb2d6f0b'
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Init extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import models and routes
from app import models
with app.app_context():
    db.create_all()

from app import routes

# Prometheus metrics 
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)
