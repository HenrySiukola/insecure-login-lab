"""
Main routes for Insecure Login Lab.

Secure branch version.

This module handles:
- profile display
- admin user management
- search
- file upload, viewing, and deletion
"""

import os

from flask import (
    Blueprint,
    redirect,
    url_for,
    render_template,
    request,
    current_app,
    session,
    send_from_directory,
)

from werkzeug.utils import secure_filename

from .db import get_db


bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"txt", "png", "jpg", "jpeg", "gif", "pdf"}


def allowed_file(filename):
    """
    Return True if the filename has an allowed extension.
    """

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_current_user():
    """
    Return the current authenticated user from the database.

    Security fix:
    Authorization is checked against server-side database state
    instead of trusting client-controlled cookie values.
    """

    user_id = session.get("user_id")

    if not user_id:
        return None

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        SELECT id, username, role
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    return cur.fetchone()


def require_admin():
    """
    Return the current user if they are an admin.

    Security fix:
    The user's role is reloaded from the database before
    granting access to admin functionality.
    """

    user = get_current_user()

    if not user:
        return None

    user_id, username, role = user

    if role != "admin":
        return None

    return user


def get_user_upload_folder():
    """
    Return the current user's upload directory.
    """

    user = get_current_user()

    upload_root = current_app.config["UPLOAD_FOLDER"]
    user_folder = os.path.join(upload_root, str(user[0]))

    os.makedirs(user_folder, exist_ok=True)

    return user_folder


@bp.route("/profile")
def profile():
    """
    Display the current user's profile page.
    """

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.index"))

    user_id, username, role = user

    return render_template(
        "profile.html",
        username=username,
        role=role
    )


@bp.route("/admin")
def admin():
    """
    Display the admin panel.
    """

    admin_user = require_admin()

    if not admin_user:
        return "Access denied", 403

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id, username, role FROM users ORDER BY id"
    )

    users = cur.fetchall()

    return render_template("admin.html", users=users)


@bp.route("/admin/change-role", methods=["POST"])
def change_role():
    """
    Change a user's role.

    Security fix:
    Admin status is verified server-side before applying changes.
    """

    admin_user = require_admin()

    if not admin_user:
        return "Access denied", 403

    user_id = request.form.get("user_id")
    new_role = request.form.get("role")

    if new_role not in ["user", "admin"]:
        return "Invalid role", 400

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        UPDATE users
        SET role = ?
        WHERE id = ?
        """,
        (new_role, user_id)
    )

    db.commit()

    return redirect(url_for("main.admin"))


@bp.route("/admin/delete-user", methods=["POST"])
def delete_user():
    """
    Delete a user account.

    Security fix:
    Admin status is verified server-side before deletion.
    """

    admin_user = require_admin()

    if not admin_user:
        return "Access denied", 403

    user_id = request.form.get("user_id")

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    db.commit()

    return redirect(url_for("main.admin"))


@bp.route("/search")
def search():
    """
    Display the search page.

    Security fix:
    Search input should be rendered escaped in the template.
    """

    q = request.args.get("q", "")

    return render_template("search.html", q=q)


@bp.route("/uploads", methods=["GET", "POST"])
def uploads():
    """
    Display and manage uploaded files.

    Security fixes:
    - require authentication
    - restrict allowed file extensions
    - sanitize filenames
    """

    if not get_current_user():
        return redirect(url_for("auth.index"))

    upload_folder = get_user_upload_folder()

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if not uploaded_file or uploaded_file.filename == "":
            return render_template(
                "uploads.html",
                error="No file selected",
                files=os.listdir(upload_folder)
            )

        if not allowed_file(uploaded_file.filename):
            return render_template(
                "uploads.html",
                error="File type is not allowed.",
                files=os.listdir(upload_folder)
            )

        filename = secure_filename(uploaded_file.filename)
        save_path = os.path.join(upload_folder, filename)

        uploaded_file.save(save_path)

        return redirect(url_for("main.uploads"))

    files = os.listdir(upload_folder)

    return render_template("uploads.html", files=files)


@bp.route("/uploads/view/<path:filename>")
def view_upload(filename):
    """
    Serve uploaded files from the current user's upload directory.

    Security fix:
    Uses Flask's safe file-serving helper instead of directly
    opening a user-controlled path.
    """

    if not get_current_user():
        return redirect(url_for("auth.index"))

    upload_folder = get_user_upload_folder()

    return send_from_directory(upload_folder, filename)


@bp.route("/uploads/delete/<path:filename>", methods=["POST"])
def delete_upload(filename):
    """
    Delete one uploaded file belonging to the current user.
    """

    if not get_current_user():
        return redirect(url_for("auth.index"))

    upload_folder = get_user_upload_folder()
    safe_filename = secure_filename(filename)

    file_path = os.path.join(upload_folder, safe_filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for("main.uploads"))


@bp.route("/uploads/delete-all", methods=["POST"])
def delete_all_uploads():
    """
    Delete all uploaded files belonging to the current user.
    """

    if not get_current_user():
        return redirect(url_for("auth.index"))

    folder = get_user_upload_folder()

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)

    return redirect(url_for("main.uploads"))