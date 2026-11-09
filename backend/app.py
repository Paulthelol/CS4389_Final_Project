import os
import psycopg
from dotenv import load_dotenv
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

load_dotenv()

import routes


ERROR_MESSAGE = "An unexpected server error occurred"


def get_session_ttl_hours():
    try:
        hours = int(os.getenv("SESSION_TTL_HOURS", "8"))
    except ValueError:
        raise RuntimeError("SESSION_TTL_HOURS must be an integer")

    if not 1 <= hours <= 168:
        raise RuntimeError("SESSION_TTL_HOURS must be between 1 and 168")

    return hours


def create_app():
    app = Flask(__name__)

    app.config["SESSION_TTL_HOURS"] = get_session_ttl_hours()

    # Automatically register exported Blueprints
    for name in routes.__all__:
        app.register_blueprint(getattr(routes, name))

    # Handle unexpected database errors.
    @app.errorhandler(psycopg.Error)
    def handle_database_error(error):
        app.logger.exception("Unexpected database error")
        return jsonify({"error": ERROR_MESSAGE}), 500

    # Handle other unexpected application errors.
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        # Preserve Flask's normal HTTP error responses.
        if isinstance(error, HTTPException):
            return error

        app.logger.exception("Unexpected application error")
        return jsonify({"error": ERROR_MESSAGE}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)