from flask import Flask, jsonify, request, abort, session, send_from_directory
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, Trail, User
from config import DevelopmentConfig, TestingConfig, ProductionConfig
from sqlalchemy import text
import requests
import logging
import os
import datetime

def create_app():
    app = Flask(__name__)

    # Secret key for session management
    app.secret_key = os.environ.get("SECRET_KEY", "ee179677c3aba6ad5fc1f2e0a8e4544a8959f5e79e3c82621f21398270c85be7")

    # Logging configuration
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Starting the application...")

    # Environment configuration
    env = os.environ.get('FLASK_ENV', 'development')
    logging.info(f"Loading configuration for {env} environment...")
  
   
    app.config.from_object(ProductionConfig)
    


    # Database and migrations setup
    db.init_app(app)
    Migrate(app, db)
    logging.info("Database initialized successfully.")

    # Swagger UI configuration
    SWAGGER_URL = '/api/docs'
    API_URL = '/swagger.json'  # Points to the local Swagger YAML file
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Trails API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    logging.info("Swagger UI registered successfully.")

    # Swagger Route for Swagger JSON
    @app.route('/swagger.json')
    def swagger_json():
        try:
            return send_from_directory('static', 'swagger.yml')
        except Exception as e:
            logging.error(f"Error serving swagger.yml: {e}")
            abort(500, description="Swagger specification file not found.")

    # External API URL for authentication
    AUTH_API_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

    # Middleware for role-based access control
    def role_required(required_role):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if 'username' not in session or 'role' not in session:
                    logging.warning("Unauthorized access attempt.")
                    abort(401, description="Unauthorized: Please log in.")
                if session['role'] != required_role:
                    logging.warning(f"Access denied for user {session['username']} with role {session['role']}.")
                    abort(403, description="Forbidden: You do not have permission to access this resource.")
                return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator

    @app.route('/test-db')
    def test_db():
        try:
            # Use SQLAlchemy's `text` function for raw SQL expressions
            result = db.session.execute(text('SELECT 1'))
            return jsonify({"message": "Database connection successful!"}), 200
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return jsonify({"error": "Database connection failed", "details": str(e)}), 500

    @app.route('/login', methods=['POST'])
    def login():
        try:
            if not request.is_json:
                logging.warning("Request does not contain valid JSON.")
                return jsonify({"error": "Request must be in JSON format."}), 400

            credentials = request.get_json()
            email = credentials.get('email')
            password = credentials.get('password')  # Assume password validation is external for now

            if not email or not password:
                return jsonify({"error": "Email and password are required."}), 400

            # Fetch the user from the database
            user = User.query.filter_by(EmailAddress=email).first()
            if not user:
                logging.warning(f"User with email {email} not found.")
                return jsonify({"error": "Invalid email or password."}), 401

            # Simulate authentication success (password validation can be added later)
            session['username'] = user.EmailAddress
            session['role'] = user.Role
            session['logged_in_at'] = datetime.datetime.utcnow().isoformat()

            logging.info(f"User {email} authenticated successfully as {user.Role}.")
            return jsonify({
                "message": "Login successful",
                "username": user.EmailAddress,
                "role": user.Role
            }), 200

        except Exception as e:
            logging.error(f"Unexpected error during login: {e}")
            return jsonify({"error": "Internal Server Error."}), 500




    # Logout Route
    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        logging.info("User logged out successfully.")
        return jsonify({"message": "Logged out successfully."}), 200

    # CRUD operations with role-based access control
    @app.route('/trails', methods=['GET'])
    def get_all_trails():
        try:
            # Retrieve all trails from the database
            trails = Trail.query.all()
            
            # Transform the list of Trail objects into a list of dictionaries
            trails_data = [
                {
                    "TrailID": trail.TrailID,
                    "TrailName": trail.TrailName,
                    "TrailRating": float(trail.TrailRating) if trail.TrailRating is not None else None,
                    "TrailDifficulty": trail.TrailDifficulty,
                    "TrailDistance": float(trail.TrailDistance),
                    "TrailEstTime": trail.TrailEstTime,
                    "TrailRouteType": trail.TrailRouteType,
                    "TrailDescription": trail.TrailDescription,
                    "LocationID": trail.LocationID
                }
                for trail in trails
            ]
            
            logging.info("All trails retrieved successfully.")
            return jsonify({"trails": trails_data}), 200
        except Exception as e:
            logging.error(f"Error fetching trails: {e}")
            abort(500, description="Internal Server Error")

    # GET a specific trail
    @app.route('/trails/<int:trail_id>', methods=['GET'])
    def get_trail(trail_id):
        try:
            trail = Trail.query.get(trail_id)
            if not trail:
                logging.warning(f"Trail with ID {trail_id} not found.")
                abort(404, description=f"Trail with ID {trail_id} not found.")
            trail_data = {
                "TrailID": trail.TrailID,
                "TrailName": trail.TrailName,
                "TrailRating": float(trail.TrailRating) if trail.TrailRating is not None else None,
                "TrailDifficulty": trail.TrailDifficulty,
                "TrailDistance": float(trail.TrailDistance),
                "TrailEstTime": trail.TrailEstTime,
                "TrailRouteType": trail.TrailRouteType,
                "TrailDescription": trail.TrailDescription,
                "LocationID": trail.LocationID
            }
            logging.info(f"Trail with ID {trail_id} retrieved successfully.")
            return jsonify(trail_data), 200
        except Exception as e:
            logging.error(f"Error fetching trail with ID {trail_id}: {e}")
            abort(500, description="Internal Server Error")

    @app.route('/trails', methods=['POST'])
    @role_required('Admin')  # Ensure only admins can create trails
    def create_trail():
        try:
            # Get the JSON data from the request
            data = request.get_json()
            if not data:
                logging.warning("No data provided in request.")
                abort(400, description="Request body cannot be empty.")

            # Validate required fields
            required_fields = ["TrailName", "TrailDifficulty", "TrailDistance", "TrailEstTime", "TrailRouteType", "TrailDescription", "LocationID"]
            for field in required_fields:
                if field not in data:
                    logging.warning(f"Missing field: {field}")
                    abort(400, description=f"Missing field: {field}")

            # Optional field: TrailRating
            trail_rating = data.get("TrailRating", None)  # Default to None if not provided

            # Create a new trail object
            new_trail = Trail(
                TrailName=data["TrailName"],
                TrailDifficulty=data["TrailDifficulty"],
                TrailDistance=data["TrailDistance"],
                TrailEstTime=data["TrailEstTime"],
                TrailRouteType=data["TrailRouteType"],
                TrailDescription=data["TrailDescription"],
                LocationID=data["LocationID"],
                TrailRating=trail_rating  # Add the rating here
            )

            # Add and commit to the database
            db.session.add(new_trail)
            db.session.commit()

            logging.info(f"Trail {new_trail.TrailName} created successfully with ID {new_trail.TrailID}.")
            return jsonify({
                "message": "Trail created successfully",
                "TrailID": new_trail.TrailID
            }), 201

        except Exception as e:
            logging.error(f"Error creating trail: {e}")
            abort(500, description="Internal Server Error")

    # PUT update a trail
    @app.route('/trails/<int:trail_id>', methods=['PUT'])
    @role_required('Admin')
    def update_trail(trail_id):
        try:
            trail = Trail.query.get(trail_id)
            if not trail:
                logging.warning(f"Trail with ID {trail_id} not found.")
                abort(404, description=f"Trail with ID {trail_id} not found.")
            data = request.get_json()
            if not data:
                logging.warning("No data provided in request.")
                abort(400, description="No data provided.")
            trail.TrailName = data.get("TrailName", trail.TrailName)
            trail.TrailRating = data.get("TrailRating", trail.TrailRating)
            trail.TrailDifficulty = data.get("TrailDifficulty", trail.TrailDifficulty)
            trail.TrailDistance = data.get("TrailDistance", trail.TrailDistance)
            trail.TrailEstTime = data.get("TrailEstTime", trail.TrailEstTime)
            trail.TrailRouteType = data.get("TrailRouteType", trail.TrailRouteType)
            trail.TrailDescription = data.get("TrailDescription", trail.TrailDescription)
            trail.LocationID = data.get("LocationID", trail.LocationID)
            db.session.commit()
            logging.info(f"Trail with ID {trail_id} updated successfully.")
            return jsonify({"message": "Trail updated successfully"}), 200
        except Exception as e:
            logging.error(f"Error updating trail with ID {trail_id}: {e}")
            abort(500, description="Internal Server Error")

    # DELETE a trail
    @app.route('/trails/<int:trail_id>', methods=['DELETE'])
    @role_required('Admin')
    def delete_trail(trail_id):
        try:
            trail = Trail.query.get(trail_id)
            if not trail:
                logging.warning(f"Trail with ID {trail_id} not found.")
                abort(404, description=f"Trail with ID {trail_id} not found.")
            db.session.delete(trail)
            db.session.commit()
            logging.info(f"Trail with ID {trail_id} deleted successfully.")
            return jsonify({"message": f"Trail with ID {trail_id} deleted successfully."}), 200
        except Exception as e:
            logging.error(f"Error deleting trail with ID {trail_id}: {e}")
            abort(500, description="Internal Server Error")

    return app

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        logging.info("User logged out successfully.")
        return jsonify({"message": "Logged out successfully."}), 200

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

