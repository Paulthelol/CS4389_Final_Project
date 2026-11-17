
import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Establish a database connection using the credentials selected
    by DB_ACCESS_MODE.

    Supported modes:
        appuser   - Connect using the restricted banking_app role.
        superuser - Connect using the PostgreSQL superuser.
    """

    access_mode = os.getenv("DB_ACCESS_MODE", "appuser").strip().lower()

    if access_mode == "appuser":
        db_user = os.getenv("POSTGRES_APP_USER", "banking_app")
        db_password = os.getenv("POSTGRES_APP_PASSWORD")

    elif access_mode == "superuser":
        db_user = os.getenv("POSTGRES_SUPERUSER")
        db_password = os.getenv("POSTGRES_SUPERUSER_PASSWORD")

    else:
        raise RuntimeError(
            "Invalid DB_ACCESS_MODE. "
            "Expected 'appuser' or 'superuser'."
        )

    if not db_user or not db_password:
        raise RuntimeError(
            f"Missing database credentials for DB_ACCESS_MODE='{access_mode}'."
        )

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=db_user,
        password=db_password,
    )


@contextmanager
def get_authenticated_connection(
    role,
    *,
    employee_id=None,
    customer_id=None
):
    """
    Establish a connection for an authenticated API request.

    The role and ID must come from a validated application session,
    not directly from client-supplied request data.
    """

    if role == "customer":
        if customer_id is None or employee_id is not None:
            raise ValueError(
                "Customer connections require only customer_id."
            )

    elif role in {"teller", "admin"}:
        if employee_id is None or customer_id is not None:
            raise ValueError(
                "Employee connections require only employee_id."
            )

    else:
        raise ValueError("Unsupported role.")

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


@contextmanager
def get_pre_auth_connection():
    """
    Establish a connection for operations performed before
    an authenticated user identity has been established.

    Currently sets the RLS role to admin so login and registration
    operations can access the necessary employee/customer records.

    WARNING:
        This grants broad row access under the current RLS policies.
        Use only for explicitly designated pre-authentication operations.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT set_config('app.current_role', 'admin', true)
                """
            )

        yield conn
