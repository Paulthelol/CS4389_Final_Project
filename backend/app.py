from flask import Flask

from routes.employees import employees_bp
from routes.customers import customers_bp
from routes.accounts import accounts_bp


def create_app():
    app = Flask(__name__)

    # Register API route groups
    app.register_blueprint(employees_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(accounts_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)