import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
import routes


def get_session_ttl_hours():
    try:
        hours = int(os.getenv("SESSION_TTL_HOURS", "8"))
    except ValueError:
        raise RuntimeError(
            "SESSION_TTL_HOURS must be an integer"
        )

    if not 1 <= hours <= 168:
        raise RuntimeError(
            "SESSION_TTL_HOURS must be between 1 and 168"
        )

    return hours

def create_app():
    app = Flask(__name__)

    app.config["SESSION_TTL_HOURS"] = get_session_ttl_hours()

    # Automatically register exported Blueprints
    for name in routes.__all__:
        app.register_blueprint(getattr(routes, name))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)