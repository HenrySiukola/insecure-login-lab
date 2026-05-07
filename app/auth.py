"""
Authentication routes for Insecure Login Lab.

Secure branch version.

This module handles:
- user registration
- login/logout
- password hashing
- Flask session creation
"""

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
)

from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_db


bp = Blueprint("auth", __name__)


@bp.route("/")
def index():
    """
    Display the login page.
    """

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user account.

    Security fixes:
    - uses parameterized SQL queries
    - stores password hashes instead of plaintext passwords
    - assigns new users the default non-admin role
    """

    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template(
            "register.html",
            error="Username and password are required."
        )

    password_hash = generate_password_hash(password)
    role = "user"

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, role)
        )
        db.commit()

    except Exception:
        return render_template(
            "register.html",
            error="Username may already exist."
        )

    return redirect(url_for("auth.index"))


@bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and create a Flask session.

    Security fixes:
    - looks up users by username only
    - verifies passwords using a password hash
    - uses parameterized SQL queries
    - does not create a custom client-controlled auth cookie
    """

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        SELECT id, username, password, role
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    row = cur.fetchone()

    if not row:
        return render_template(
            "login.html",
            error="Unknown credentials"
        )

    user_id, db_username, stored_password_hash, role = row

    if not check_password_hash(stored_password_hash, password):
        return render_template(
            "login.html",
            error="Unknown credentials"
        )

    session.clear()
    session["user_id"] = user_id
    session["username"] = db_username

    return redirect(url_for("main.profile"))


@bp.route("/logout")
def logout():
    """
    Log out the current user by clearing the Flask session.
    """

    session.clear()

    return redirect(url_for("auth.index"))