from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
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

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app import models
        db.create_all()
        from app import routes  

    return app
