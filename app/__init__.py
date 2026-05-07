"""
Application factory for Insecure Login Lab.

Secure branch version.

This module creates and configures the Flask application,
registers blueprints, sets up database/upload paths, and exposes
the current logged-in user to templates.
"""

import os

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

from .db import init_app, get_db

csrf = CSRFProtect()
talisman = Talisman()


def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # In production, load this from an environment variable.
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),

        DATABASE=os.path.join(app.instance_path, "lab.db"),
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),

        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,  # Set True when running over HTTPS.
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_PERMANENT=False,
    )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.context_processor
    def inject_user():
        """
        Make the current logged-in user available inside templates.

        The role is reloaded from the database so templates do not rely
        on stale or client-controlled authorization data.
        """

        if "user_id" not in session:
            return {"current_user": None}

        db = get_db()
        cur = db.cursor()

        cur.execute(
            """
            SELECT id, username, role
            FROM users
            WHERE id = ?
            """,
            (session["user_id"],)
        )

        user = cur.fetchone()

        if not user:
            return {"current_user": None}

        user_id, username, role = user

        return {
            "current_user": {
                "user_id": user_id,
                "username": username,
                "role": role,
            }
        }

    init_app(app)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    csp = {
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self'",
        "img-src": "'self' data:",
        "font-src": "'self'",
        "object-src": "'none'",
        "base-uri": "'self'",
        "frame-ancestors": "'none'",
    }

    csrf.init_app(app)
    talisman.init_app(app, content_security_policy=csp)

    return app