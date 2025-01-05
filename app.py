from flask import Flask, jsonify, request, abort, send_from_directory
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db
from config import Config
import logging

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Load configuration
    app.config.from_object(Config)

    # Initialize database and migrations
    db.init_app(app)
    Migrate(app, db)

    # Register Swagger UI blueprint
    SWAGGER_URL = '/api/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # URL where Swagger UI is served
        API_URL,      # URL for the Swagger spec
        config={'app_name': "Trails API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Routes
    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the Trails API!"})

    @app.route('/swagger.json')
    def swagger_json():
        # Ensure 'static/swagger.yml' exists and contains your Swagger spec
        return send_from_directory('static', 'swagger.yml')

    # Error Handlers
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)
