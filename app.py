import requests
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, Trail
from sqlalchemy.orm import Session
from config import DevelopmentConfig, TestingConfig, ProductionConfig
import logging
import os
import re

def create_app():
    app = Flask(__name__)

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
    SWAGGER_URL = app.config['SWAGGER_URL']
    API_URL = app.config['API_URL']
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Trails API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    logging.info("Swagger UI registered successfully.")

    # External API URL for authentication
    AUTH_API_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

    # Authentication Route
    @app.route('/login', methods=['POST'])
    def login():
        AUTH_API_URL = 'https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users'
        try:
            credentials = request.json
            if not credentials or 'email' not in credentials or 'password' not in credentials:
                logging.warning("Invalid request body for login.")
                return jsonify({"error": "Invalid request body. Email and password are required."}), 400

            # Send POST request to authentication API
            response = requests.post(AUTH_API_URL, json=credentials)

            if response.status_code == 200:
                try:
                    auth_status = response.json()
                    logging.info(f"Authenticated successfully: {auth_status}")
                    if auth_status[1] == "True":
                        return jsonify({"message": "Login successful", "email": credentials['email']}), 200
                    else:
                        logging.warning(f"Authentication failed for user {credentials['email']}.")
                        return jsonify({"error": "Authentication failed"}), 401
                except requests.JSONDecodeError:
                    logging.error("Response is not valid JSON.")
                    return jsonify({"error": "Invalid response from authentication server"}), 500
            else:
                logging.error(f"Authentication failed with status code {response.status_code}")
                return jsonify({"error": "Authentication failed"}), response.status_code
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            return jsonify({"error": "Internal Server Error"}), 500

    # Other routes (index, trails CRUD, etc.)
    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the Trails API!"})

    @app.route('/swagger.json')
    def swagger_json():
        try:
            return send_from_directory('static', 'swagger.yml')
        except Exception as e:
            logging.error(f"Error serving swagger.yml: {e}")
            abort(500, description="Swagger specification file not found.")

    # Placeholder for other CRUD operations for trails
    # Implement additional GET, POST, DELETE, and PUT routes as needed

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)
