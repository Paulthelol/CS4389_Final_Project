import psycopg
from flask import Blueprint, g, jsonify, request

from database import get_connection
from decorators import employee_required, role_required

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
        "role": row[2]
    }
    
# CREATE employee
@employees_bp.route("", methods=["POST"])
@role_required("admin")
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
                    RETURNING employee_id, username, role;
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
@role_required("admin")
def get_employees():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employee_id, username, role
                FROM employees
                ORDER BY employee_id;
                """
            )
            employees = cur.fetchall()
            

    return jsonify([employee_to_json(row) for row in employees]), 200


# READ one employee
@employees_bp.route("/<int:employee_id>", methods=["GET"])
@employee_required
def get_employee(employee_id):
    user = g.current_user

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employee_id, username, role
                FROM employees
                WHERE employee_id = %s
                    AND (%s = 'admin' OR employee_id = %s);
                """,
                (employee_id, user["role"], user["id"])
            )
            employee = cur.fetchone()

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(employee_to_json(employee)), 200


# UPDATE employee username
@employees_bp.route("/<int:employee_id>", methods=["PUT"])
@employee_required
def update_employee(employee_id):
    user = g.current_user
    data = request.get_json(silent=True) or {}
    username = data.get("username")

    if not isinstance(username, str):
        return jsonify({"error": "Username is required"}), 400

    username = username.strip()
    if not username or len(username) > 50:
        return jsonify({"error": "Invalid username"}), 400
        
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE employees
                    SET username = %s
                    WHERE employee_id = %s 
                        AND (%s = 'admin' OR employee_id = %s)
                    RETURNING employee_id, username, role;
                    """,
                    (username, employee_id, user["role"], user["id"])
                )
                employee = cur.fetchone()
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                return jsonify({"error": "An employee with that ID already exists"}), 409

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(employee_to_json(employee)), 200


# DELETE employee
@employees_bp.route("/<int:employee_id>", methods=["DELETE"])
@role_required("admin")
def delete_employee(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM employees
                WHERE employee_id = %s
                RETURNING employee_id;
                """,
                (employee_id,)
            )
            employee = cur.fetchone()

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify({"message": "Employee has been deleted"}), 200
