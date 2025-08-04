from flask import Flask, jsonify, request
from app import app,db
import jwt
from app.models import User
from app.models import Organisation
from app.models import UserOrganisation
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import uuid


@app.route("/")
def home_page():
    return """
    <html>
      <head>
        <title>Inkomoko Auth API</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 2rem; background-color: #f8f9fa; }
          h1 { color: #333; }
          ul { padding-left: 1rem; }
          li { margin-bottom: 0.5rem; }
          code { background-color: #eee; padding: 2px 4px; border-radius: 3px; }
        </style>
      </head>
      <body>
        <h1>Welcome to the Inkomoko Auth API</h1>
        <p>This is a lightweight authentication and organisation management API built with Flask and PostgreSQL.</p>
        <p>It supports user registration, login, JWT-based authentication, and basic organisation management.</p>

        <h2>Available Endpoints</h2>
        <ul>
          <li><strong>POST</strong> <code>/auth/register</code> - Register a new user and create default organisation</li>
          <li><strong>POST</strong> <code>/auth/login</code> - Log in and receive JWT token</li>
          <li><strong>GET</strong> <code>/api/users/&lt;userId&gt;</code> - Retrieve user profile</li>
          <li><strong>GET</strong> <code>/api/organisations</code> - List user’s organisations <em>(JWT required)</em></li>
          <li><strong>GET</strong> <code>/api/organisations/&lt;orgId&gt;</code> - Get organisation details <em>(JWT required)</em></li>
          <li><strong>POST</strong> <code>/api/organisations</code> - Create new organisation <em>(JWT required)</em></li>
          <li><strong>POST</strong> <code>/api/organisations/&lt;orgId&gt;/users</code> - Add user to organisation</li>
        </ul>

        <p>For full documentation, visit the <code>README.md</code> in the repo.</p>
      </body>
    </html>
    """


# Function to add errors to a list
def add_error_to_list(errors_list, field, message):
    errors_list.append({
        "field": field,
        "message": message
    })


def generate_jwt_token(user_id):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(), 
            'sub': str(user_id)
        }
        jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        return jwt_token
    except Exception as e:
        return "Cannot generate session token"

# Registers a user and creates a default organisation
@app.route("/auth/register", methods=['POST'])
def register_user():
    data = request.json
    errors_list = []

    # Validating required fields
    if not data.get('firstName'):
        add_error_to_list(errors_list, field="firstName", message="First name is required")
    if not data.get('lastName'):
        add_error_to_list(errors_list, field="lastName", message="Last name is required")
    if not data.get('email'):
        add_error_to_list(errors_list, field="email", message="Email is required")
    if not data.get('password'):
        add_error_to_list(errors_list, field="password", message="Password is required")
    
    # Check if email is already registered
    if User.query.filter_by(email=data['email']).first():
        add_error_to_list(errors_list, field="email", message="Email Address already in use")

    # If there are validation errors, return 400 status code with errors
    if errors_list:
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "errors": errors_list
        }), 400

    # Hash the password before storing
    hashed_password = generate_password_hash(data['password'])

    # Create a new user object
    new_user = User(
        userid=str(uuid.uuid4()),
        firstname=data['firstName'],
        lastname=data['lastName'],
        email=data['email'],
        password=hashed_password,
        phone=data.get('phone')
    )

    # Create organization name based on user's first name
    org_name = f"{new_user.firstname}'s organisation"

    try:
        # Add user and organization creation to a single transaction
        with db.session.begin_nested():
            db.session.add(new_user)
            db.session.flush()  # Ensure new_user gets an id before using it in org creation

            # Create the organization associated with the new user
            new_org = Organisation(
                orgid=str(uuid.uuid4()),
                name=org_name,
                description=f"{org_name} description"
            )
            db.session.add(new_org)

            # Associate user with organization
            user_org = UserOrganisation(userid=new_user.userid, orgid=new_org.orgid)
            db.session.add(user_org)

        db.session.commit()

        # Debug print statements
        print(f"New User ID: {new_user.userid}")
        print(f"New Org ID: {new_org.orgid}")

        # Generate JWT token for the new user
        jwt_token = generate_jwt_token(new_user.userid)

        # Return successful response with JWT token and user data
        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": jwt_token,
                "user": {
                    "userId": str(new_user.userid),
                    "firstName": new_user.firstname,
                    "lastName": new_user.lastname,
                    "email": new_user.email,
                    "phone": new_user.phone,
                }
            }
        }), 201 
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Registration unsuccessful",
            "error": str(e)
        }), 500
# Logs in a user. When you log in, you can select an organisation to interact with
@app.route("/auth/login", methods=['POST'])
def login_user():
    data = request.json

    # Retrieve user from database based on email
    existing_user = User.query.filter_by(email=data['email']).first()

    # Check if user exists
    if not existing_user:
        return jsonify({"message": "User not found"}), 404

    # Compare hashed password from database with provided password
    if not check_password_hash(existing_user.password, data['password']):
        return jsonify({"message": "Incorrect password"}), 401

    # Generate JWT token for authentication
    jwt_token = generate_jwt_token(existing_user.userid)

    # Prepare successful response
    response_successful = {
        "status": "success",
        "message": "Login successful",
        "data": {
            "accessToken": jwt_token,
            "user": {
                "userId": existing_user.userid,
                "firstName": existing_user.firstname,
                "lastName": existing_user.lastname,
                "email": existing_user.email,
                "phone": existing_user.phone
            }
        }
    }

    return jsonify(response_successful), 200

# A user gets their own record or user record in organisations they belong to or created [PROTECTED]
@app.route("/api/users/<id>", methods=['GET'])
def get_users_by_id(id):
    try:
        # Query user data based on the provided id
        user = User.query.get(id)

        # Check if user exists
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Prepare successful response
        response_successful = {
            "status": "success",
            "message": "User found",
            "data": {
                "userid": user.userid,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "phone": user.phone
            }
        }

        return jsonify(response_successful), 200

    except Exception as e:
        # Handle exceptions and rollback session on error
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

# Gets all the organisations the user belongs to or created [PROTECTED]
@app.route("/api/organisations", methods=['GET'])
@jwt_required()
def get_organizations():
    # Get the user ID from the JWT token
    userid = get_jwt_identity()

    try:
        # Query organizations where the user is a member
        user_organizations = db.session.query(Organisation).join(UserOrganisation).filter(UserOrganisation.userid == userid).all()
        print(user_organizations)

        # Prepare organizations data
        organizations = [{
            "orgId": org.orgid,
            "name": org.name,
            "description": org.description if org.description else ""
        } for org in user_organizations]

        response_successful = {
            "status": "success",
            "message": "Organizations retrieved successfully",
            "data": {
                "organisation": organizations
            }
        }

        return jsonify(response_successful), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve organizations",
            "error": str(e)
        }), 500

# The logged-in user gets a single organisation record [PROTECTED]
@app.route("/api/organisations/<orgId>", methods=['GET'])
@jwt_required()
def get_organization_by_id(orgId):
    # Get usser ID from JWT token
    userid = get_jwt_identity()
    try:
        # Query organization data based on the provided id
        organization = Organisation.query.get(orgId)

        # Check if organization exists
        if not organization:
            return jsonify({"message": "Organization not found"}), 404

        # Prepare successful response
        response_successful = {
            "status": "success",
            "message": "Organization found",
            "data": {
                "orgId": organization.orgid,
                "name": organization.name,
                "description": organization.description if organization.description else ""
            }
        }

        return jsonify(response_successful), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve organization",
            "error": str(e)
        }), 500
    response_successful = {
        "status": "success",
        "message": "<message>",
        "data": {
            "orgId": orgId,
            "name": "string",
            "description": "string",
        }
    }
    try:
        db.session.query(orgId)
        db.session.commit()
        return jsonify(response_successful)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

# A user can create their new organisation [PROTECTED]
@app.route("/api/organisations", methods=['POST'])
@jwt_required()
def create_organization():
    try:
        data = request.json

        # Extract data from JSON request
        name = data.get('name')
        description = data.get('description')

        # Validate required fields
        if not name:
            return jsonify({"message": "Name is required"}), 400

        # Create new Organisation object
        new_organization = Organisation(
            orgid=str(uuid.uuid4()),
            name=name,
            description=description
        )

        # Add to session and commit to database
        db.session.add(new_organization)
        db.session.commit()

        # Prepare successful response
        response_successful = {
            "status": "success",
            "message": "Organization created successfully",
            "data": {
                "orgId": new_organization.orgid,  
                "name": new_organization.name,
                "description": new_organization.description if new_organization.description else ""
            }
        }

        return jsonify(response_successful), 201  # HTTP status code for created

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Failed to create organization",
            "error": str(e)
        }), 500
    
# Adds a user to a particular organisation
@app.route("/api/organisations/<orgId>/users", methods=['POST'])
def add_user_to_organization(orgId):
    try:
        data = request.json

        # Extract data from JSON request
        userid = data.get('userId')

        # Validate required fields
        if not userid:
            return jsonify({"message": "User ID is required"}), 400

        # Check if the organization exists
        organization = Organisation.query.filter_by(orgid=orgId).first()
        if not organization:
            return jsonify({
                "status": "error",
                "message": "Organization not found",
                "error": f"Organization with orgId {orgId} does not exist"
            }), 404

        # Create a new UserOrganisation object
        new_user_organization = UserOrganisation(
            userid=userid,
            orgid=orgId
        )

        # Add to session and commit to database
        db.session.add(new_user_organization)
        db.session.commit()

        # Prepare successful response
        response_successful = {
            "status": "success",
            "message": "User added to organization successfully",
            "data": {
                "userId": new_user_organization.userid,
                "orgId": new_user_organization.orgid
            }
        }

        return jsonify(response_successful), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Failed to add user to organization",
            "error": str(e)
        }), 500