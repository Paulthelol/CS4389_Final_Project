import os

import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# Use for authenticated requests.
# The backend should derive the role and ID from a validated session token.
@contextmanager
def get_authenticated_connection(role, *, employee_id=None, customer_id=None):
    if role == "customer":
        if customer_id is None or employee_id is not None:
            raise ValueError("Customer connections require only customer_id")
    elif role in {"teller", "admin"}:
        if employee_id is None or customer_id is not None:
            raise ValueError("Employee connections require only employee_id")
    else:
        raise ValueError("Unsupported role")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    set_config('app.current_role', %s, true),
                    set_config('app.current_employee_id', %s, true),
                    set_config('app.current_customer_id', %s, true)
                """,
                (
                    role,
                    "" if employee_id is None else str(employee_id),
                    "" if customer_id is None else str(customer_id),
                ),
            )
        yield conn

# Use ONLY for pre-authentication operations such as login and registration,
# when no validated employee/customer identity exists yet.
#
# Temporarily sets the application role to admin, granting access to all rows permitted 
# by admin employee RLS policies. Misuse could bypass authorization checks.
#
# TODO: We might consider using a separate, restricted PostgreSQL database
# role with access only to specific SECURITY DEFINER authentication/registration functions.
# This would provide clearer separation between pre-auth and admin operations.
@contextmanager
def get_pre_auth_connection():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.current_role', 'admin', true)"
            )
        yield conn