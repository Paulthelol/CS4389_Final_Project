import hashlib
import secrets

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
    
# CREATE employee registration token
@employees_bp.route("", methods=["POST"])
@role_required("admin")
def create_employee():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    role = data.get("role")
    if role not in ("teller", "admin"):
        return jsonify({"error": "Invalid employee role"}), 400

    # Generate a random, one-time registration token.
    # Store only the token hash in the database.
    setup_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(setup_token.encode("utf-8")).hexdigest()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO employee_setup_tokens (role, token_hash, expires_at)
                VALUES (%s, %s, NOW() + INTERVAL '24 hours')
                RETURNING expires_at;
                """,
                (role, token_hash)
            )

            expires_at = cur.fetchone()[0]

    # Return the original token so the admin can provide it to the employee.
    # It cannot be retrieved again.
    return jsonify({
        "message": "Employee registration token created",
        "setup_token": setup_token,
        "role": role,
        "expires_at": expires_at.isoformat()
    }), 201


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
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400
    
    username = data.get("username")
    if not isinstance(username, str):
        return jsonify({"error": "Username is required"}), 400

    username = username.strip()
    if not username or len(username) > 50:
        return jsonify({"error": "Invalid username"}), 400

    try: 
        with get_connection() as conn:
            with conn.cursor() as cur:
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
        return jsonify({"error": "An employee with that username already exists"}), 409

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(employee_to_json(employee)), 200


# DELETE employee
@employees_bp.route("/<int:employee_id>", methods=["DELETE"])
@role_required("admin")
def delete_employee(employee_id):
    user = g.current_user
    if employee_id == user["id"]:
        return jsonify({"error": "You cannot delete your own employee account"}), 400
    try:
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

    except psycopg.errors.ForeignKeyViolation:
        return jsonify({"error": "Employee cannot be deleted because they have associated transactions"}), 409

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify({"message": "Employee has been deleted"}), 200
