import psycopg
from flask import Blueprint, jsonify, request
from database import get_connection


employees_bp = Blueprint(
    "employees",
    __name__,
    url_prefix="/employees"
)

#json representation of employee data
def employee_to_json(row):
    return {
        "employee_id": row[0],
        "username": row[1],
        "password_hash": row[2],
        "role": row[3]
    }
    
# CREATE employee
@employees_bp.route("", methods=["POST"])
def create_employee():
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employee_id")
    username = data.get("username")
    password_hash = data.get("password_hash")
    role = data.get("role")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO employees (employee_id, username, password_hash, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING employee_id, username, password_hash, role;
                    """,
                    (employee_id, username, password_hash, role)
                )
                employee = cur.fetchone()
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                return jsonify({"error": "An employee with that ID already exists"}), 409

    return jsonify(employee_to_json(employee)), 201


# READ all employees
@employees_bp.route("", methods=["GET"])
def get_employees():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employee_id, username, password_hash, role
                FROM employees
                ORDER BY employee_id;
                """
            )
            employees = cur.fetchall()
            

    return jsonify([employee_to_json(row) for row in employees]), 200


# READ one employee
@employees_bp.route("/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employee_id, username, password_hash, role
                FROM employees
                WHERE employee_id = %s;
                """,
                (employee_id,)
            )
            employee = cur.fetchone()

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(employee_to_json(employee)), 200


# UPDATE employee username
@employees_bp.route("/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}
    username = data.get("username")

    if not username:
        return jsonify({"error": "username is required"}), 400
        
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE employees
                    SET username = %s
                    WHERE employee_id = %s
                    RETURNING employee_id, username, password_hash, role;
                    """,
                    (username, employee_id)
                )
                employee = cur.fetchone()
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                jsonify({"error": "An employee with that ID already exists"}), 409

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(employee_to_json(employee)), 200


# DELETE employee
@employees_bp.route("/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM employees
                WHERE employee_id = %s
                RETURNING employee_id;
                """,
                (employee_id)
            )
            employee = cur.fetchone()

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify({"message": "Employee has been deleted"}), 200
