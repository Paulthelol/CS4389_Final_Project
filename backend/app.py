import os
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


def get_bool_env(name, default):
    value = os.getenv(name, default).strip().lower()

    if value in ("true", "1", "yes", "on"):
        return True

    if value in ("false", "0", "no", "off"):
        return False

    raise RuntimeError(f"{name} must be a Boolean value")


def create_app():
    app = Flask(__name__)

    app.config["SESSION_TTL_HOURS"] = get_session_ttl_hours()

    demo_mode = get_bool_env("DEMO_MODE", "false")
    security_enabled = get_bool_env("API_SECURITY_ENABLED", "true")

    # Never allow security to be disabled outside demo mode.
    if not security_enabled and not demo_mode:
        raise RuntimeError("API security cannot be disabled unless DEMO_MODE is enabled")

    app.config["DEMO_MODE"] = demo_mode
    app.config["API_SECURITY_ENABLED"] = security_enabled

    if not security_enabled:
        app.logger.warning("API SECURITY IS DISABLED. Vulnerable demo mode is active.")

    # Automatically register exported Blueprints
    for name in routes.__all__:
        app.register_blueprint(getattr(routes, name))

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