from flask import Flask, jsonify, request, abort, send_from_directory
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, Trail
from config import DevelopmentConfig, TestingConfig, ProductionConfig
import logging
import os

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Starting the application...")

    # Dynamically load configuration based on environment
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

    # Initialize database and migrations
    db.init_app(app)
    Migrate(app, db)
    logging.info("Database initialized successfully.")

    # Register Swagger UI blueprint
    SWAGGER_URL = app.config['SWAGGER_URL']
    API_URL = app.config['API_URL']
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Trails API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    logging.info("Swagger UI registered successfully.")

    # Routes
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

    @app.route('/trails', methods=['GET', 'POST'])
    def trails():
        if request.method == 'GET':
            try:
                # Pagination parameters
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)

                # Add order_by clause for MSSQL compatibility
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
                required_fields = ["TrailName", "TrailDifficulty", "TrailDistance", "TrailEstTime", "TrailRouteType", "TrailDescription", "LocationID"]
                if not data or not all(field in data for field in required_fields):
                    abort(400, description="Missing required fields.")

                new_trail = Trail(
                    TrailName=data["TrailName"],
                    TrailDifficulty=data["TrailDifficulty"],
                    TrailDistance=data["TrailDistance"],
                    TrailEstTime=data["TrailEstTime"],
                    TrailRouteType=data["TrailRouteType"],
                    TrailDescription=data["TrailDescription"],
                    LocationID=data["LocationID"]
                )
                db.session.add(new_trail)
                db.session.commit()

                return jsonify({"message": "Trail created successfully", "TrailID": new_trail.TrailID}), 201
            except Exception as e:
                logging.error(f"Error creating trail: {e}")
                abort(500, description="Internal Server Error")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)
