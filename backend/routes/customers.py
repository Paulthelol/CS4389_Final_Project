from flask import Blueprint
from database.connection import get_connection


customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
)


# CREATE customer
@customers_bp.route("", methods=["POST"])
def create_customer():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Create a new customer
            pass

    # TODO: Return created customer
    pass


# READ all customers
@customers_bp.route("", methods=["GET"])
def get_customers():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Retrieve all customers
            pass

    # TODO: Return customers
    pass


# READ one customer
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Retrieve customer by ID
            pass

    # TODO: Return customer
    pass


# UPDATE customer
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Update customer by ID
            pass

    # TODO: Return updated customer
    pass


# DELETE customer
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Delete customer by ID
            pass

    # TODO: Return confirmation
    pass