import os

from flask import (
    Blueprint,
    redirect,
    url_for,
    render_template,
    request,
    current_app,
)

from .db import get_db

# Main application blueprint
bp = Blueprint("main", __name__)


def get_insecure_auth():
    """
    Read and parse the intentionally insecure authentication cookie.

    Cookie format:
        user_id|username|role

    SECURITY NOTE:
    This implementation is intentionally vulnerable because:
    - the cookie is fully client-controlled
    - the cookie is not signed
    - authorization data is trusted directly
    - delimiter injection can manipulate parsing
    """

    # Read custom authentication cookie
    cookie = request.cookies.get("lab_auth")

    if not cookie:
        return None

    # Intentionally insecure parsing
    parts = cookie.split("|")

    if len(parts) < 3:
        return None

    return {
        "user_id": parts[0],
        "username": parts[1],
        "role": parts[2],
    }


def require_admin():
    """
    Verify that the current user has the admin role.

    SECURITY NOTE:
    This implementation intentionally trusts the role
    directly from the client-controlled cookie instead
    of validating it server-side.
    """

    user = get_insecure_auth()

    if not user:
        return None

    # Intentionally insecure:
    # trusts authorization data from the cookie
    if user["role"] != "admin":
        return None

    return user


def get_user_upload_folder():
    """
    Return the current user's upload directory.

    A separate folder is created for each user based on
    their user ID.
    """

    user = get_insecure_auth()

    upload_root = current_app.config["UPLOAD_FOLDER"]

    # Create per-user upload directory
    user_folder = os.path.join(upload_root, str(user["user_id"]))

    os.makedirs(user_folder, exist_ok=True)

    return user_folder


@bp.route("/profile")
def profile():
    """
    Display the currently logged-in user's profile page.
    """

    user = get_insecure_auth()

    if not user:
        return redirect(url_for("auth.index"))

    return render_template(
        "profile.html",
        username=user["username"],
        role=user["role"]
    )


@bp.route("/admin")
def admin():
    """
    Display the admin panel.

    The admin panel allows privileged users to:
    - view all users
    - change user roles
    - delete accounts
    """

    admin_user = require_admin()

    if not admin_user:
        return "Access denied", 403

    db = get_db()
    cur = db.cursor()

    # Retrieve all users from the database
    cur.execute(
        "SELECT id, username, role FROM users ORDER BY id"
    )

    users = cur.fetchall()

    return render_template("admin.html", users=users)


@bp.route("/admin/change-role", methods=["POST"])
def change_role():
    """
    Change a user's role.

    SECURITY NOTE:
    This endpoint intentionally lacks CSRF protection.
    """

    admin_user = require_admin()

    if not admin_user:
        return "Access denied", 403

    user_id = request.form.get("user_id")
    new_role = request.form.get("role")

    # Basic validation
    if new_role not in ["user", "admin"]:
        return "Invalid role", 400

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "UPDATE users SET role = ? WHERE id = ?",
        (new_role, user_id)
    )

    db.commit()

    return redirect(url_for("main.admin"))


@bp.route("/search")
def search():
    """
    Vulnerable search page.

    SECURITY NOTE:
    The template intentionally renders user input
    unsafely for reflected XSS practice.
    """

    q = request.args.get("q", "")

    return render_template("search.html", q=q)


@bp.route("/uploads", methods=["GET", "POST"])
def uploads():
    """
    Display and manage uploaded files.

    SECURITY NOTE:
    The upload system intentionally allows dangerous
    file types such as HTML for stored XSS practice.
    """

    if not get_insecure_auth():
        return redirect(url_for("auth.index"))

    upload_folder = get_user_upload_folder()

    # Handle file uploads
    if request.method == "POST":

        uploaded_file = request.files.get("file")

        if not uploaded_file or uploaded_file.filename == "":
            return render_template(
                "uploads.html",
                error="No file selected",
                files=os.listdir(upload_folder)
            )

        # Intentionally insecure:
        # filename is used directly without sanitization
        save_path = os.path.join(
            upload_folder,
            uploaded_file.filename
        )

        uploaded_file.save(save_path)

        return redirect(url_for("main.uploads"))

    # Display uploaded files
    files = os.listdir(upload_folder)

    return render_template("uploads.html", files=files)


@bp.route("/uploads/view/<path:filename>")
def view_upload(filename):
    """
    Serve uploaded files back to the user.

    SECURITY NOTE:
    This implementation intentionally uses unsafe
    file path construction for path traversal practice.
    """

    if not get_insecure_auth():
        return redirect(url_for("auth.index"))

    upload_folder = get_user_upload_folder()

    # Intentionally insecure path handling
    file_path = os.path.join(upload_folder, filename)

    # Intentionally unsafe direct file access
    with open(file_path, "rb") as f:
        content = f.read()

    return content


@bp.route("/uploads/delete/<path:filename>", methods=["POST"])
def delete_upload(filename):
    """
    Delete a single uploaded file.

    SECURITY NOTE:
    This endpoint intentionally lacks CSRF protection.
    """

    if not get_insecure_auth():
        return redirect(url_for("auth.index"))

    upload_folder = get_user_upload_folder()

    file_path = os.path.join(upload_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for("main.uploads"))


@bp.route("/admin/delete-user", methods=["POST"])
def delete_user():
    """
    Delete a user account.

    SECURITY NOTE:
    This endpoint intentionally lacks CSRF protection.
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


@bp.route("/uploads/delete-all", methods=["POST"])
def delete_all_uploads():
    """
    Delete all uploaded files belonging to the current user.

    SECURITY NOTE:
    This endpoint intentionally lacks CSRF protection.
    """

    if not get_insecure_auth():
        return redirect(url_for("auth.index"))

    folder = get_user_upload_folder()

    # Delete every file in the user's upload directory
    for f in os.listdir(folder):
        os.remove(os.path.join(folder, f))

    return redirect(url_for("main.uploads"))