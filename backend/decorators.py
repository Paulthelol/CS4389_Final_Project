import hashlib
from functools import wraps

from flask import g, jsonify, request

from database import get_connection


def token_required(func):
    """Require a valid, unexpired bearer token."""

    @wraps(func)
    def decorated(*args, **kwargs):
        # Extract the bearer token.
        parts = request.headers.get("Authorization", "").split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Authentication required"}), 401

        token_hash = hashlib.sha256(parts[1].encode()).hexdigest()

        # Find the session and associated user.
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.employee_id, s.customer_id, e.role
                    FROM sessions s
                    LEFT JOIN employees e
                        ON s.employee_id = e.employee_id
                    WHERE s.token_hash = %s
                      AND s.expires_at > NOW()
                    """,
                    (token_hash,)
                )
                session = cur.fetchone()

        if not session:
            return jsonify({"error": "Invalid or expired token"}), 401

        employee_id, customer_id, role = session

        # Store the authenticated user's information for this request.
        g.current_user = {
            "type": "employee" if employee_id is not None else "customer",
            "id": employee_id if employee_id is not None else customer_id,
            "role": role
        }

        return func(*args, **kwargs)

    return decorated


def employee_required(func):
    """Require the authenticated user to be an employee."""

    @wraps(func)
    def decorated(*args, **kwargs):
        if g.current_user["type"] != "employee":
            return jsonify({"error": "Employee access required"}), 403

        return func(*args, **kwargs)

    return token_required(decorated)


def role_required(role):
    """Require the authenticated employee to have a specific role."""

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            user = g.current_user

            if user["type"] != "employee" or user["role"] != role:
                return jsonify({"error": "Insufficient permissions"}), 403

            return func(*args, **kwargs)

        return token_required(decorated)

    return decorator