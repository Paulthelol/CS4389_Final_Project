from flask import Blueprint
from database import get_connection


employees_bp = Blueprint(
    "employees",
    __name__,
    url_prefix="/employees"
)


# CREATE employee
@employees_bp.route("", methods=["POST"])
def create_employee():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Create a new employee
            pass

    # TODO: Return created employee
    pass


# READ all employees
@employees_bp.route("", methods=["GET"])
def get_employees():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Retrieve all employees
            pass

    # TODO: Return employees
    pass


# READ one employee
@employees_bp.route("/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Retrieve employee by ID
            pass

    # TODO: Return employee
    pass


# UPDATE employee
@employees_bp.route("/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Update employee by ID
            pass

    # TODO: Return updated employee
    pass


# DELETE employee
@employees_bp.route("/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Delete employee by ID
            pass

    # TODO: Return confirmation
    pass