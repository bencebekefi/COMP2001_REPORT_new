from flask import Flask, jsonify, request, abort, send_from_directory
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, Trail
from sqlalchemy.orm import Session
from config import DevelopmentConfig, TestingConfig, ProductionConfig
import logging
import os

def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Starting the application...")
    
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

   
    db.init_app(app)
    Migrate(app, db)
    logging.info("Database initialized successfully.")


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

    @app.route('/trails/<int:trail_id>', methods=['DELETE'])
    def delete_trail(trail_id):
        try:
            # Fetch the trail by its ID
            trail = Trail.query.get(trail_id)
            if not trail:
                logging.warning(f"Trail with ID {trail_id} not found.")
                abort(404, description=f"Trail with ID {trail_id} not found.")

            # Delete the trail
            db.session.delete(trail)
            db.session.commit()

            logging.info(f"Trail with ID {trail_id} deleted successfully.")
            return jsonify({"message": f"Trail with ID {trail_id} deleted successfully."}), 200

        except Exception as e:
            logging.error(f"Error deleting trail with ID {trail_id}: {e}")
            abort(500, description="Internal Server Error")


    @app.route('/trails/<int:trail_id>', methods=['GET'])
    def get_trail_by_id(trail_id):
        try:
            logging.debug(f"Fetching trail with ID: {trail_id}")

            # Attempt to fetch the trail
            trail = db.session.get(Trail, trail_id)

            if not trail:
                logging.warning(f"Trail with ID {trail_id} not found.")
                return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

            # Prepare the response
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
            logging.error(f"Error fetching trail with ID {trail_id}: {e}", exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route('/trails/<int:trail_id>', methods=['PUT'])
    def update_trail(trail_id):
        try:
            logging.debug(f"Updating trail with ID: {trail_id}")

            # Fetch the trail by its ID
            trail = Trail.query.filter_by(TrailID=trail_id).first()

            if not trail:
                logging.warning(f"Trail with ID {trail_id} not found.")
                return jsonify({"error": f"Trail with ID {trail_id} not found."}), 404

            # Parse the request JSON data
            data = request.get_json()

            if not data:
                logging.warning("No data provided in request.")
                return jsonify({"error": "No data provided."}), 400

            # Update the trail fields based on the input data
            if "TrailName" in data:
                trail.TrailName = data["TrailName"]

            if "TrailRating" in data:
                try:
                    trail.TrailRating = float(data["TrailRating"])
                    if not (0 <= trail.TrailRating <= 5):
                        raise ValueError("TrailRating must be between 0 and 5.")
                except ValueError as e:
                    logging.error(f"Invalid TrailRating: {e}")
                    return jsonify({"error": "TrailRating must be a decimal between 0 and 5."}), 400

            if "TrailDifficulty" in data:
                if data["TrailDifficulty"] not in ["Easy", "Moderate", "Hard"]:
                    logging.error("Invalid TrailDifficulty value.")
                    return jsonify({"error": "TrailDifficulty must be one of 'Easy', 'Moderate', 'Hard'."}), 400
                trail.TrailDifficulty = data["TrailDifficulty"]

            if "TrailDistance" in data:
                trail.TrailDistance = float(data["TrailDistance"])

            if "TrailEstTime" in data:
                trail_est_time = data["TrailEstTime"]
                import re
                if not re.match(r'^\d{2}h \d{2}m$', trail_est_time):
                    logging.error("Invalid TrailEstTime format.")
                    return jsonify({
                            "error": "TrailEstTime must be in the format 'XXh XXm', e.g., '01h 30m'."
                    }), 400
            trail.TrailEstTime = trail_est_time


            if "TrailRouteType" in data:
                if data["TrailRouteType"] not in ["Circular", "Loop", "Out & Back", "Point to Point"]:
                    logging.error("Invalid TrailRouteType value.")
                    return jsonify({"error": "TrailRouteType must be one of 'Circular', 'Loop', 'Out & Back', 'Point to Point'."}), 400
                trail.TrailRouteType = data["TrailRouteType"]

            if "TrailDescription" in data:
                trail.TrailDescription = data["TrailDescription"]

            if "LocationID" in data:
                trail.LocationID = int(data["LocationID"])

            # Commit the changes to the database
            db.session.commit()

            logging.info(f"Trail with ID {trail_id} updated successfully.")

            # Prepare and return the updated trail details
            updated_trail = {
                "TrailID": trail.TrailID,
                "TrailName": trail.TrailName,
                "TrailRating": float(trail.TrailRating) if trail.TrailRating is not None else None,
                "TrailDifficulty": trail.TrailDifficulty,
                "TrailDistance": float(trail.TrailDistance),
                "TrailEstTime": trail.TrailEstTime,
                "TrailRouteType": trail.TrailRouteType,
                "TrailDescription": trail.TrailDescription,
                "LocationID": trail.LocationID,
            }

            return jsonify(updated_trail), 200

        except Exception as e:
            logging.error(f"Error updating trail with ID {trail_id}: {e}", exc_info=True)
            return jsonify({"error": "Internal Server Error"}), 500


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)
