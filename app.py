"""
VulnChain -- Browser-Only Software Vulnerability CTF
CSCE A465 -- Computer & Network Security

WARNING: This application is INTENTIONALLY VULNERABLE.
         DO NOT deploy on any network-accessible host.
"""

import os
import json
from flask import (
    Flask, request, session, redirect, url_for,
    render_template, render_template_string, flash, jsonify,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "SUPERSECRETKEY_d3v_0nly"

# Simulated "database" of registered users
USERS = {
    "guest": {"password": "guest123", "role": "user"},
}

# Flag
FLAG_TEXT = "FLAG{s0ftwar3_s3cur1ty_A465}"
FLAG_PATH = "secret/flag.txt"

# Directory for downloadable files
FILES_DIR = os.path.join(os.path.dirname(__file__), "public_files")

# ---------------------------------------------------------------------------
# Stage 1  --  Information Disclosure (Debug Endpoint)
# ---------------------------------------------------------------------------

@app.route("/api/debug")
def api_debug():
    """Debug endpoint that should have been removed before production."""
    return jsonify({
        "app_name": "VulnChain Internal Portal",
        "version": "0.9.3-dev",
        "debug": True,
        "secret_key": app.secret_key,
        "database": {
            "host": "localhost",
            "user": "admin",
            "password": "admin_p@ss!",
        },
        "hidden_endpoint": "/register",
        "flag_path": FLAG_PATH,
        "note": "TODO: remove this endpoint before production deployment",
    })

# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    user = USERS.get(username)
    if user and user["password"] == password:
        session["username"] = username
        session["role"] = user["role"]
        flash(f"Welcome back, {username}.")
        return redirect(url_for("dashboard"))

    flash("Invalid credentials. Try again.")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# Stage 2  --  Mass Assignment (Registration)
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # --- THE VULNERABILITY ---
    # Blindly accept every form field the client sends,
    # including "role" which is not in the visible form.
    user_data = {key: val for key, val in request.form.items()}

    username = user_data.get("username", "").strip()
    password = user_data.get("password", "").strip()

    if not username or not password:
        flash("Username and password are required.")
        return redirect(url_for("register"))

    if username in USERS:
        flash("Username already taken.")
        return redirect(url_for("register"))

    # Default role is "user", but if the client sent role=admin ...
    role = user_data.get("role", "user")

    USERS[username] = {"password": password, "role": role}
    flash(f"Account created. You can now log in as '{username}'.")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
def dashboard():
    username = session.get("username")
    role = session.get("role")
    if not username:
        flash("Please log in first.")
        return redirect(url_for("index"))
    return render_template("dashboard.html", username=username, role=role)

# ---------------------------------------------------------------------------
# Stage 3  --  Server-Side Template Injection (SSTI)
# ---------------------------------------------------------------------------

@app.route("/admin")
def admin_panel():
    username = session.get("username")
    role = session.get("role")
    if not username:
        flash("Please log in first.")
        return redirect(url_for("index"))
    if role != "admin":
        flash("Access denied. Admin privileges required.")
        return redirect(url_for("dashboard"))
    return render_template("admin.html", username=username)


@app.route("/admin/announce", methods=["POST"])
def announce():
    role = session.get("role")
    if role != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    content = request.form.get("content", "")

    # --- THE VULNERABILITY ---
    # User input is passed directly to render_template_string(),
    # allowing Jinja2 template expressions to execute on the server.
    try:
        rendered = render_template_string(content)
    except Exception as e:
        rendered = f"<span class='error'>Template Error: {e}</span>"

    return render_template("admin.html",
                           username=session.get("username"),
                           announcement=rendered,
                           raw_input=content)

# ---------------------------------------------------------------------------
# Stage 4  --  Path Traversal (File Viewer)
# ---------------------------------------------------------------------------

@app.route("/files")
def files():
    name = request.args.get("name", "")

    if not name:
        # Show file listing
        available = []
        if os.path.isdir(FILES_DIR):
            available = os.listdir(FILES_DIR)
        return render_template("files.html", files=available, content=None)

    # --- THE VULNERABILITY ---
    # The filename is concatenated directly without sanitization,
    # allowing directory traversal with ../
    filepath = os.path.join(FILES_DIR, name)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = f"Error: file '{name}' not found."
    except Exception as e:
        content = f"Error reading file: {e}"

    return render_template("files.html", files=[], content=content,
                           filename=name)

# ---------------------------------------------------------------------------
# Flag Check
# ---------------------------------------------------------------------------

@app.route("/check-flag", methods=["POST"])
def check_flag():
    submitted = request.form.get("flag", "").strip()
    if submitted == FLAG_TEXT:
        return render_template("victory.html", flag=FLAG_TEXT)
    flash("Incorrect flag. Try again.")
    return redirect(url_for("files"))

# ---------------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create dummy files for the file browser
    os.makedirs(FILES_DIR, exist_ok=True)
    dummy_files = {
        "report.pdf": "Q3 Internal Security Audit -- CONFIDENTIAL\nNo critical vulnerabilities found.\n(This is a dummy file for demonstration.)",
        "employees.csv": "id,name,department\n1,Alice,Engineering\n2,Bob,Marketing\n3,Charlie,Security",
        "changelog.txt": "v0.9.3 - added admin announcement feature\nv0.9.2 - added file browser\nv0.9.1 - initial release",
    }
    for fname, fcontent in dummy_files.items():
        fpath = os.path.join(FILES_DIR, fname)
        if not os.path.exists(fpath):
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fcontent)

    # Create the flag file
    os.makedirs("secret", exist_ok=True)
    flag_file = os.path.join("secret", "flag.txt")
    if not os.path.exists(flag_file):
        with open(flag_file, "w", encoding="utf-8") as f:
            f.write(FLAG_TEXT)

    print("\n" + "=" * 60)
    print("  VulnChain -- Browser-Only Software Vulnerability CTF")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    print("  [!] This app is intentionally insecure.")
    print("  [!] For educational use only (CSCE A465).")
    print("=" * 60 + "\n")

    app.run(debug=True)
