import hashlib
import os
import secrets

import psycopg
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from flask import Blueprint, current_app, jsonify, request

from database import get_connection


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

password_hasher = PasswordHasher()


# EMPLOYEE REGISTER
@auth_bp.route("/employees/register", methods=["POST"])
def employee_register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    username = data.get("username")
    password = data.get("password")

    # Validate request fields.
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password are required"}), 400

    username = username.strip()
    if not username or len(username) > 30:
        return jsonify({"error": "Invalid username"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if len(password.encode("utf-8")) > 1024:
        return jsonify({"error": "Password is too long"}), 400

    # Hash password using Argon2 (automatically generates a random salt).
    password_hash = password_hasher.hash(password)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO employees (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    RETURNING employee_id, username, role;
                    """,
                    (username, password_hash, "teller")
                )

                employee = cur.fetchone()

    except psycopg.errors.UniqueViolation:
        return jsonify({"error": "Username already exists"}), 409

    return jsonify({
        "message": "Registration successful",
        "employee": {
            "employee_id": employee[0],
            "username": employee[1],
            "role": employee[2]
        }
    }), 201


# EMPLOYEE LOGIN
@auth_bp.route("/employees/login", methods=["POST"])
def employee_login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password are required"}), 400

    # Look up employee credentials
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employee_id, username, password_hash, role
                FROM employees
                WHERE username = %s;
                """,
                (username.strip(),)
            )

            employee = cur.fetchone()

    if employee is None:
        return jsonify({"error": "Invalid username or password"}), 401

    # Verify password against stored Argon2 hash.
    try:
        password_hasher.verify(employee[2], password)
    except (VerificationError, InvalidHashError):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate a random session token and store only its hash.
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    session_hours = current_app.config["SESSION_TTL_HOURS"]

    # Save session and expiration.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessions (employee_id, token_hash, expires_at)
                VALUES (
                    %s,
                    %s,
                    NOW() + (%s * INTERVAL '1 hour')
                )
                RETURNING expires_at;
                """,
                (employee[0], token_hash, session_hours)
            )

            expires_at = cur.fetchone()[0]

    return jsonify({
        "message": "Login successful",
        "session_token": token,
        "expires_at": expires_at.isoformat(),
        "employee": {
            "employee_id": employee[0],
            "username": employee[1],
            "role": employee[3]
        }
    }), 200


#==============================================================================

"""
Employee generates a one-time setup token to be provided to the customer
after the employee has entered the customer's information into the database.

Customer uses this token to register a password for their login credentials.
"""
# CUSTOMER PASSWORD SETUP
@auth_bp.route("/customers/register", methods=["POST"])
def customer_register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    email = data.get("email")
    setup_token = data.get("setup_token")
    password = data.get("password")

    # Validate request fields.
    if not all(
        isinstance(value, str)
        for value in (email, setup_token, password)
    ):
        return jsonify({"error": "Email, setup token, and password are required"}), 400

    email = email.strip().lower()
    if not email or not setup_token or not password:
        return jsonify({"error": "Email, setup token, and password are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if len(password.encode("utf-8")) > 1024:
        return jsonify({"error": "Password is too long"}), 400

    # Hash the supplied setup token and new password.
    token_hash = hashlib.sha256(setup_token.encode("utf-8")).hexdigest()
    password_hash = password_hasher.hash(password)

    # Verify the token and update the existing customer atomically.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.setup_token_id, c.customer_id
                FROM customer_setup_tokens AS t
                JOIN customers AS c
                    ON c.customer_id = t.customer_id
                WHERE LOWER(c.email) = %s
                  AND t.token_hash = %s
                  AND t.expires_at > NOW()
                  AND t.used_at IS NULL
                  AND c.password_hash IS NULL
                FOR UPDATE OF t, c;
                """,
                (email, token_hash)
            )

            setup = cur.fetchone()

            if setup is None:
                return jsonify({"error": "Invalid or expired registration details"}), 400

            setup_token_id, customer_id = setup

            cur.execute(
                """
                UPDATE customers
                SET password_hash = %s
                WHERE customer_id = %s
                  AND password_hash IS NULL;
                """,
                (password_hash, customer_id)
            )

            if cur.rowcount != 1:
                return jsonify({"error": "Unable to complete registration"}), 409

            cur.execute(
                """
                UPDATE customer_setup_tokens
                SET used_at = NOW()
                WHERE setup_token_id = %s;
                """,
                (setup_token_id,)
            )

    return jsonify({"message": "Password setup successful"}), 201

# CUSTOMER LOGIN
@auth_bp.route("/customers/login", methods=["POST"])
def customer_login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email and password are required"}), 400
    
    email = email.strip().lower()
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Look up an existing customer by email.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer_id, email, password_hash
                FROM customers
                WHERE LOWER(email) = %s;
                """,
                (email,)
            )
            customer = cur.fetchone()

    # Reject customers who do not exist or have not set up credentials.
    if customer is None or customer[2] is None:
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify password against stored Argon2 hash.
    try:
        password_hasher.verify(customer[2], password)
    except (VerificationError, InvalidHashError):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate a random session token and store only its hash.
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    session_hours = current_app.config["SESSION_TTL_HOURS"]

    # Save session and expiration.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessions (
                    customer_id,
                    token_hash,
                    expires_at
                )
                VALUES (
                    %s,
                    %s,
                    NOW() + (%s * INTERVAL '1 hour')
                )
                RETURNING expires_at;
                """,
                (customer[0], token_hash, session_hours)
            )
            expires_at = cur.fetchone()[0]

    return jsonify({
        "message": "Login successful",
        "session_token": token,
        "expires_at": expires_at.isoformat(),
        "customer": {
            "customer_id": customer[0],
            "email": customer[1]
        }
    }), 200


#==============================================================================

# LOGOUT
@auth_bp.route("/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Authentication required"}), 401

    token = parts[1]
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sessions
                WHERE token_hash = %s;
                """,
                (token_hash,)
            )

    return jsonify({"message": "Logout successful"}), 200