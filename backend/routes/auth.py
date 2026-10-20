import hashlib
import os
import secrets

import psycopg
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from flask import Blueprint, jsonify, request

from database import get_connection


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

password_hasher = PasswordHasher()


# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    # TODO: Validate registration input
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password are required"}), 400

    username = username.strip()

    if not username or len(username) > 50:
        return jsonify({"error": "Invalid username"}), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 12 characters"
        }), 400

    if len(password.encode("utf-8")) > 1024:
        return jsonify({"error": "Password is too long"}), 400

    # Hash password using Argon2 (automatically generates a random salt)
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


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

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

    # Verify password against stored Argon2 hash
    try:
        password_hasher.verify(employee[2], password)
    except VerificationError:
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate an opaque session token
    token = secrets.token_urlsafe(32)

    # Store only the SHA-256 hash of the token
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    session_hours = int(os.getenv("SESSION_TTL_HOURS", "8"))

    if not 1 <= session_hours <= 168:
        return jsonify({"error": "Invalid server session configuration"}), 500

    # Save session and expiration
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


#TODO: Add sessions table to database schema

"""
CREATE TABLE sessions (
    session_id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""