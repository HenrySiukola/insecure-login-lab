"""
Database utilities for Insecure Login Lab.

Secure branch version.

This module manages:
- SQLite database connections
- database initialization
- Flask application database lifecycle hooks
"""

import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    """
    Return the current SQLite database connection.

    The connection is stored in Flask's `g` object so that
    a single connection can be reused during the request.
    """

    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"]
        )

    return g.db


def close_db(e=None):
    """
    Close the current database connection if one exists.

    This function is automatically called at the end of
    each Flask request.
    """

    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """
    Initialize the SQLite database.

    The existing users table is deleted and recreated.

    Security fix:
    Demo passwords are stored as password hashes instead
    of plaintext values.
    """

    database_path = current_app.config["DATABASE"]

    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    db = sqlite3.connect(database_path)
    cur = db.cursor()

    cur.execute("DROP TABLE IF EXISTS users")

    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cur.execute(
        """
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """,
        (
            "admin",
            generate_password_hash("admin123"),
            "admin",
        )
    )

    cur.execute(
        """
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """,
        (
            "alice",
            generate_password_hash("password"),
            "user",
        )
    )

    db.commit()
    db.close()


def init_app(app):
    """
    Register database cleanup handlers with the Flask app.
    """

    app.teardown_appcontext(close_db)