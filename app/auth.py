"""
Authentication routes for Insecure Login Lab.

This module contains intentionally insecure implementations of:
- authentication
- session handling
- cookie handling
- user registration

SECURITY NOTE:
Several vulnerabilities are intentionally included for
educational security testing purposes.
"""

from flask import (
    make_response,
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
)

from .db import get_db


# Authentication blueprint
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

    SECURITY NOTE:
    This route intentionally contains several vulnerabilities:
    - SQL injection
    - plaintext password storage
    - insufficient input validation
    """

    # Display registration form
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # New accounts are created with the default user role
    role = "user"

    if not username or not password:
        return render_template(
            "register.html",
            error="Username and password are required."
        )

    db = get_db()
    cur = db.cursor()

    try:
        # Intentionally insecure SQL query construction
        cur.execute(
            f"INSERT INTO users (username, password, role) "
            f"VALUES ('{username}', '{password}', '{role}')"
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
    Authenticate a user and create an insecure authentication cookie.

    SECURITY NOTE:
    This route intentionally contains:
    - SQL injection
    - insecure cookie handling
    - plaintext password comparison
    """

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    db = get_db()
    cur = db.cursor()

    # Intentionally vulnerable SQL query
    query = (
        f"SELECT id, username, password, role "
        f"FROM users "
        f"WHERE username = '{username}' "
        f"AND password = '{password}'"
    )

    cur.execute(query)

    row = cur.fetchone()

    if not row:
        return render_template(
            "login.html",
            error="Unknown credentials"
        )

    user_id, db_username, db_password, role = row

    # Store user information in Flask session
    session["user_id"] = user_id
    session["username"] = db_username
    session["role"] = role

    response = make_response(
        redirect(url_for("main.profile"))
    )

    # Intentionally insecure custom authentication cookie
    response.set_cookie(
        "lab_auth",
        f"{user_id}|{db_username}|{role}",
        httponly=False
    )

    return response


@bp.route("/logout")
def logout():
    """
    Log out the current user.

    Clears both:
    - Flask session data
    - custom authentication cookie
    """

    session.clear()

    response = make_response(
        redirect(url_for("auth.index"))
    )

    response.delete_cookie("lab_auth")

    return response