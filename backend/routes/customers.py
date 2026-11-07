import psycopg
from flask import Blueprint, jsonify, request

from database import get_connection


customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
)


def customer_to_json(row):
    """Convert a customer database row into the public API representation."""
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
        max_length = 255 if field == "email" else 100
        if field == "ssn":
            max_length = 11
        if len(value) > max_length:
            return None, f"{field} is too long"
        values[field] = value

    return values, None


# CREATE customer
@customers_bp.route("", methods=["POST"])
def create_customer():
    data, error = validate_customer_data(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO customers (first_name, last_name, ssn, email)
                    VALUES (%s, %s, %s, %s)
                    RETURNING customer_id, first_name, last_name, ssn, email;
                    """,
                    (data["first_name"], data["last_name"], data["ssn"], data.get("email")),
                )
                customer = cur.fetchone()
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                return jsonify({"error": "A customer with that SSN or email already exists"}), 409

    return jsonify(customer_to_json(customer)), 201


# READ all customers
@customers_bp.route("", methods=["GET"])
def get_customers():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer_id, first_name, last_name, ssn, email
                FROM customers
                ORDER BY customer_id;
                """
            )
            customers = cur.fetchall()

    return jsonify([customer_to_json(row) for row in customers]), 200


# READ one customer
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer_id, first_name, last_name, ssn, email
                FROM customers
                WHERE customer_id = %s;
                """,
                (customer_id,),
            )
            customer = cur.fetchone()

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_to_json(customer)), 200


# UPDATE customer
@customers_bp.route("/<int:customer_id>", methods=["PUT", "PATCH"])
def update_customer(customer_id):
    data, error = validate_customer_data(
        request.get_json(silent=True) or {}, partial=True
    )
    if error:
        return jsonify({"error": error}), 400

    columns = [field for field in ("first_name", "last_name", "ssn", "email") if field in data]
    assignments = ", ".join(f"{column} = %s" for column in columns)
    values = [data[column] for column in columns]
    values.append(customer_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    f"""
                    UPDATE customers
                    SET {assignments}
                    WHERE customer_id = %s
                    RETURNING customer_id, first_name, last_name, ssn, email;
                    """,
                    values,
                )
                customer = cur.fetchone()
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                return jsonify({"error": "A customer with that SSN or email already exists"}), 409

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_to_json(customer)), 200


# DELETE customer
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM customers WHERE customer_id = %s RETURNING customer_id;",
                (customer_id,),
            )
            deleted = cur.fetchone()

    if deleted is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({"message": "Customer deleted"}), 200
