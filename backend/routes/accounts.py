from flask import Blueprint
from database.connection import get_connection


accounts_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/accounts"
)


# CREATE account
@accounts_bp.route("", methods=["POST"])
def create_account():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Create a new account
            pass

    # TODO: Return created account
    pass


# READ all accounts
@accounts_bp.route("", methods=["GET"])
def get_accounts():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Retrieve all accounts
            pass

    # TODO: Return accounts
    pass


# READ one account
@accounts_bp.route("/<int:account_id>", methods=["GET"])
def get_account(account_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Retrieve account by ID
            pass

    # TODO: Return account
    pass


# UPDATE account
@accounts_bp.route("/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Update account by ID
            pass

    # TODO: Return updated account
    pass


# DELETE account
@accounts_bp.route("/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # TODO: Delete account by ID
            pass

    # TODO: Return confirmation
    pass