from flask import Flask, jsonify, request, abort, session, send_from_directory
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, Trail
from config import DevelopmentConfig, TestingConfig, ProductionConfig
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
    if env == 'development':
        app.config.from_object(DevelopmentConfig)
    elif env == 'testing':
        app.config.from_object(TestingConfig)
    elif env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        logging.error("Invalid environment specified. Defaulting to DevelopmentConfig.")
        app.config.from_object(DevelopmentConfig)

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

    # Login Route
    @app.route('/login', methods=['POST'])
    def login():
        try:
            if not request.is_json:
                logging.warning("Request does not contain valid JSON.")
                return jsonify({"error": "Request must be in JSON format."}), 400

            credentials = request.get_json()
            logging.debug(f"Request JSON: {credentials}")

            if not credentials:
                logging.warning("Request body is empty or invalid.")
                return jsonify({"error": "Request body cannot be empty."}), 400

            if 'email' not in credentials:
                logging.warning("Missing 'email' in request body.")
                return jsonify({"error": "Missing 'email' in request body."}), 400

            if 'password' not in credentials:
                logging.warning("Missing 'password' in request body.")
                return jsonify({"error": "Missing 'password' in request body."}), 400

            auth_payload = {
                "email": credentials['email'],
                "password": credentials['password']
            }

            response = requests.post(AUTH_API_URL, json=auth_payload)
            logging.debug(f"Auth API response status: {response.status_code}")
            logging.debug(f"Auth API response text: {response.text}")

            if response.status_code == 200:
                try:
                    auth_status = response.json()
                    logging.debug(f"Auth API response data: {auth_status}")

                    if isinstance(auth_status, list) and len(auth_status) >= 2:
                        role = auth_status[0]
                        is_verified = auth_status[1]

                        if is_verified == "True":
                            session['username'] = credentials['email']  
                            session['role'] = role
                            session['logged_in_at'] = datetime.datetime.utcnow().isoformat()

                            logging.info(f"User {credentials['email']} authenticated successfully as {role}.")
                            return jsonify({
                                "message": "Login successful",
                                "username": credentials['email'],
                                "role": role
                            }), 200
                        else:
                            logging.warning(f"Authentication failed for user {credentials['email']}.")
                            return jsonify({"error": "Authentication failed. Check your credentials."}), 401
                    else:
                        logging.error(f"Unexpected auth API response format: {auth_status}")
                        return jsonify({"error": "Unexpected response format from authentication API."}), 500
                except Exception as e:
                    logging.error(f"Error parsing authentication API response: {e}")
                    return jsonify({"error": "Error parsing response from authentication API."}), 500
            else:
                logging.error(f"Authentication API error with status code {response.status_code}: {response.text}")
                return jsonify({"error": f"Authentication API error: {response.status_code}"}), response.status_code

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
    @app.route('/trails', methods=['GET', 'POST'])
    def trails():
        if request.method == 'GET':
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                pagination = Trail.query.order_by(Trail.TrailID).paginate(page=page, per_page=per_page)
                trails = [{
                    "TrailID": trail.TrailID,
                    "TrailName": trail.TrailName,
                    "TrailDifficulty": trail.TrailDifficulty,
                    "TrailDistance": float(trail.TrailDistance),
                    "TrailEstTime": trail.TrailEstTime,
                    "TrailRouteType": trail.TrailRouteType,
                    "TrailDescription": trail.TrailDescription,
                    "LocationID": trail.LocationID
                } for trail in pagination.items]
                return jsonify({
                    "data": trails,
                    "total": pagination.total,
                    "page": pagination.page,
                    "pages": pagination.pages
                }), 200
            except Exception as e:
                logging.error(f"Error fetching trails: {e}")
                abort(500, description="Internal Server Error")
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    abort(400, description="Request body cannot be empty.")
                new_trail = Trail(
                    TrailName=data['TrailName'],
                    TrailDifficulty=data['TrailDifficulty'],
                    TrailDistance=data['TrailDistance'],
                    TrailEstTime=data['TrailEstTime'],
                    TrailRouteType=data['TrailRouteType'],
                    TrailDescription=data.get('TrailDescription'),
                    LocationID=data['LocationID']
                )
                db.session.add(new_trail)
                db.session.commit()
                return jsonify({"message": "Trail created successfully."}), 201
            except KeyError as e:
                abort(400, description=f"Missing required field: {str(e)}")
            except Exception as e:
                logging.error(f"Error creating trail: {e}")
                abort(500, description="Internal Server Error")

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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000) 