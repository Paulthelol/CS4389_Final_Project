from flask import Flask

import routes


def create_app():
    app = Flask(__name__)

    # Automatically register exported Blueprints
    for name in routes.__all__:
        app.register_blueprint(getattr(routes, name))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)