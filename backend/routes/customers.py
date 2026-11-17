import hashlib
import secrets
import re
from contextlib import contextmanager

import psycopg
from flask import Blueprint, current_app, g, jsonify, request

from database.connection import (
    get_authenticated_connection,
    get_pre_auth_connection,
)
from decorators import token_required, employee_required


customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
)


@contextmanager
def get_customer_connection():
    """
    Return a database connection with the appropriate RLS context.

    Employee requests use the authenticated employee's role and ID.
    Customer requests use the authenticated customer's ID.
    When API security is disabled, the decorators simulate an admin,
    so use the admin database context.
    """
    if not current_app.config.get("API_SECURITY_ENABLED", True):
        with get_pre_auth_connection() as conn:
            yield conn
        return

    user = g.current_user

    if user["type"] == "employee":
        with get_authenticated_connection(
            user["role"],
            employee_id=user["id"]
        ) as conn:
            yield conn

    elif user["type"] == "customer":
        with get_authenticated_connection(
            "customer",
            customer_id=user["id"]
        ) as conn:
            yield conn

    else:
        raise RuntimeError("Unsupported authenticated user type")


def customer_to_json(row):
    """Convert a masked customer database row into the public API representation."""
    return {
        "customer_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "ssn": row[3],
        "email": row[4],
    }


def validate_customer_data(data, *, partial=False):
    """Validate customer input and return normalized values or an error message."""
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    fields = ("first_name", "last_name", "ssn", "email")
    if partial:
        if not any(field in data for field in fields):
            return None, "At least one customer field is required"
    else:
        required = ("first_name", "last_name", "ssn")
        missing = [field for field in required if field not in data]
        if missing:
            return None, "first_name, last_name, and ssn are required"

    values = {}
    for field in fields:
        if field not in data:
            continue

        value = data[field]
        if field == "email" and value is None:
            values[field] = None
            continue

        if not isinstance(value, str) or not value.strip():
            return None, f"{field} must be a non-empty string"

        value = value.strip()
        if field in ("first_name", "last_name"):
            if len(value) > 100:
                return None, f"{field} is too long"

        elif field == "ssn":
            if not re.fullmatch(r"\d{3}-\d{2}-\d{4}", value):
                return None, "ssn must use the format XXX-XX-XXXX"

        elif field == "email":
            if len(value) > 255:
                return None, "email is too long"
            value = value.lower()

        values[field] = value

    return values, None


# CREATE customer (employees only; generate a setup token for customer password registration)
@customers_bp.route("", methods=["POST"])
@employee_required
def create_customer():
    data = request.get_json(silent=True)
    values, error = validate_customer_data(data)
    if error:
        return jsonify({"error": error}), 400

    # Email is required because customer registration uses it
    # to identify the customer associated with the setup token
    if not values.get("email"):
        return jsonify({"error": "email is required"}), 400

    # Generate a random, one-time registration token.
    # Store only the token hash in the database.
    setup_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(setup_token.encode("utf-8")).hexdigest()

    try:
        with get_customer_connection() as conn:
            with conn.cursor() as cur:
                # Create the customer record without returning the raw SSN.
                cur.execute(
                    """
                    INSERT INTO customers (first_name, last_name, ssn, email)
                    VALUES (%s, %s, %s, %s)
                    RETURNING customer_id;
                    """,
                    (
                        values["first_name"],
                        values["last_name"],
                        values["ssn"],
                        values["email"]
                    )
                )

                customer_id = cur.fetchone()[0]

                # Store the hashed setup token with a 24-hour expiration.
                cur.execute(
                    """
                    INSERT INTO customer_setup_tokens
                        (customer_id, token_hash, expires_at)
                    VALUES (%s, %s, NOW() + INTERVAL '24 hours')
                    RETURNING expires_at;
                    """,
                    (customer_id, token_hash)
                )

                expires_at = cur.fetchone()[0]

                # Retrieve the customer through the masked view.
                cur.execute(
                    """
                    SELECT customer_id, first_name, last_name, ssn, email
                    FROM customers_masked
                    WHERE customer_id = %s;
                    """,
                    (customer_id,)
                )

                customer = cur.fetchone()

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "A customer with that SSN or email already exists"
        }), 409

    # Return the original token so the employee can provide it to the customer.
    # It cannot be retrieved again.
    return jsonify({
        "message": "Customer created successfully",
        "customer": customer_to_json(customer),
        "setup_token": setup_token,
        "expires_at": expires_at.isoformat()
    }), 201


# READ all customers
@customers_bp.route("", methods=["GET"])
@employee_required
def get_customers():
    with get_customer_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer_id, first_name, last_name, ssn, email
                FROM customers_masked
                ORDER BY customer_id;
                """
            )
            customers = cur.fetchall()

    return jsonify([customer_to_json(row) for row in customers]), 200


# READ one customer
@customers_bp.route("/<int:customer_id>", methods=["GET"])
@token_required
def get_customer(customer_id):
    user = g.current_user

    with get_customer_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer_id, first_name, last_name, ssn, email
                FROM customers_masked
                WHERE customer_id = %s
                    AND (%s = 'employee' OR customer_id = %s);
                """,
                (customer_id, user["type"], user["id"]),
            )
            customer = cur.fetchone()

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_to_json(customer)), 200


# UPDATE customer
@customers_bp.route("/<int:customer_id>", methods=["PUT", "PATCH"])
@employee_required
def update_customer(customer_id):
    data, error = validate_customer_data(
        request.get_json(silent=True),
        partial=True
    )
    if error:
        return jsonify({"error": error}), 400

    columns = [
        field
        for field in ("first_name", "last_name", "ssn", "email")
        if field in data
    ]
    assignments = ", ".join(f"{column} = %s" for column in columns)
    values = [data[column] for column in columns]
    values.append(customer_id)

    try:
        with get_customer_connection() as conn:
            with conn.cursor() as cur:
                # Update the underlying table without returning the raw SSN.
                cur.execute(
                    f"""
                    UPDATE customers
                    SET {assignments}
                    WHERE customer_id = %s
                    RETURNING customer_id;
                    """,
                    values,
                )

                updated = cur.fetchone()

                if updated is not None:
                    # Retrieve the updated customer through the masked view.
                    cur.execute(
                        """
                        SELECT customer_id, first_name, last_name, ssn, email
                        FROM customers_masked
                        WHERE customer_id = %s;
                        """,
                        (updated[0],)
                    )

                    customer = cur.fetchone()
                else:
                    customer = None

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "A customer with that SSN or email already exists"
        }), 409

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_to_json(customer)), 200


# DELETE customer
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
    user = g.current_user

    try:
        with get_customer_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM customers
                    WHERE customer_id = %s
                        AND (%s = 'employee' OR customer_id = %s)
                    RETURNING customer_id;
                    """,
                    (customer_id, user["type"], user["id"]),
                )

                deleted = cur.fetchone()

    except psycopg.errors.ForeignKeyViolation:
        return jsonify({
            "error": "Customer cannot be deleted while associated accounts exist"
        }), 409

    if deleted is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({"message": "Customer deleted"}), 200