"""
Application factory for Insecure Login Lab.

This module creates and configures the Flask application,
registers blueprints, sets up upload/database paths, and exposes
the intentionally insecure current user context to templates.

SECURITY NOTE:
Several configuration values are intentionally insecure for
educational purposes.
"""

import os

from flask import Flask, request

from .db import init_app


def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # Intentionally weak hardcoded secret for lab purposes.
        SECRET_KEY="dev-secret",

        # Store the SQLite database in Flask's instance folder.
        DATABASE=os.path.join(app.instance_path, "lab.db"),

        # Store uploaded files in the instance folder.
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),

        # Intentionally insecure cookie settings for XSS/cookie-theft practice.
        SESSION_COOKIE_HTTPONLY=False,
        SESSION_COOKIE_SECURE=False,

        # Use browser-session cookies instead of persistent cookies.
        SESSION_PERMANENT=False,
    )

    # Ensure required instance directories exist.
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.context_processor
    def inject_user():
        """
        Make the current user available inside templates.

        The user is parsed from the intentionally insecure `lab_auth`
        cookie and exposed as `current_user`.

        SECURITY NOTE:
        This trusts client-controlled cookie values directly.
        """

        cookie = request.cookies.get("lab_auth")

        if not cookie:
            return {"current_user": None}

        parts = cookie.split("|")

        if len(parts) < 3:
            return {"current_user": None}

        return {
            "current_user": {
                "user_id": parts[0],
                "username": parts[1],
                "role": parts[2],
            }
        }

    # Register database cleanup handlers.
    init_app(app)

    # Register authentication routes.
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Register main application routes.
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app