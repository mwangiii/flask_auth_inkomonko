from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from prometheus_flask_exporter import PrometheusMetrics 

import os

# Initialize Flask application
app = Flask(__name__)

# ADD Prometheus Exporter
metrics = PrometheusMetrics(app)



# Load database configuration from database.ini using config function
db_params = config()
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
# connect the postgress to localhost db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '4f8b31dc8ee3437486e3424bcb2d6f0b'
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import models (this should be done before calling db.create_all())
from app import models

# Create database tables if they do not exist
with app.app_context():
    db.create_all()

# Import routes
from app import routes

# This will allow you to manage database migrations using Flask-Migrate
if __name__ == '__main__':
    app.run()
    