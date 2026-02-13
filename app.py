"""
Bypass -- Browser-Only Software Vulnerability CTF
CSCE A465 -- Computer & Network Security

WARNING: This application is INTENTIONALLY VULNERABLE.
         DO NOT deploy on any network-accessible host.
"""

import os
import json
from markupsafe import escape
from flask import (
    Flask, request, session, redirect, url_for,
    render_template, render_template_string, flash, jsonify,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "SUPERSECRETKEY_d3v_0nly"
app.config["FLAG_PATH"] = "secret/flag.txt"
app.config["FILES_ENDPOINT"] = "/files"

# Simulated "database" of registered users
USERS = {
    "guest": {"password": "guest123", "role": "user"},
}

# Flag
FLAG_TEXT = "FLAG{s0ftwar3_s3cur1ty_A465}"
FLAG_PATH = "secret/flag.txt"

# Directory for downloadable files
FILES_DIR = os.path.join(os.path.dirname(__file__), "public_files")


def is_secure():
    """Check if the app is running in secure mode."""
    return session.get("secure_mode", False)


# ---------------------------------------------------------------------------
# Secure Mode Toggle
# ---------------------------------------------------------------------------

@app.route("/toggle-secure")
def toggle_secure():
    """Switch between vulnerable and secure mode. Resets the session."""
    switching_to_secure = not session.get("secure_mode", False)
    session.clear()
    session["secure_mode"] = switching_to_secure
    if switching_to_secure:
        flash("Switched to secure mode. Try the same exploits again.")
    else:
        flash("Switched to vulnerable mode.")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Context Processor -- make secure_mode available in all templates
# ---------------------------------------------------------------------------

@app.context_processor
def inject_mode():
    return {"secure_mode": is_secure()}


# ---------------------------------------------------------------------------
# Stage 1  --  Information Disclosure (Debug Endpoint)
# ---------------------------------------------------------------------------

@app.route("/api/debug")
def api_debug():
    """Debug endpoint that should have been removed before production."""
    # SECURE: endpoint is removed entirely
    if is_secure():
        return jsonify({"error": "endpoint not found"}), 404

    return jsonify({
        "app_name": "Bypass Internal Portal",
        "version": "0.9.3-dev",
        "debug": True,
        "hidden_endpoint": "/register",
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
    secure = session.get("secure_mode", False)
    session.clear()
    session["secure_mode"] = secure
    flash("Logged out.")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# Stage 2  --  Mass Assignment (Registration)
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        flash("Username and password are required.")
        return redirect(url_for("register"))

    if username in USERS:
        flash("Username already taken.")
        return redirect(url_for("register"))

    # SECURE: only accept username and password, ignore everything else
    if is_secure():
        role = "user"
    else:
        # --- THE VULNERABILITY ---
        # Blindly accept the "role" field from the client
        role = request.form.get("role", "user")

    USERS[username] = {"password": password, "role": role}

    # Auto-login after registration
    session["username"] = username
    session["role"] = role

    if is_secure() and request.form.get("role"):
        flash(f"Account created as 'user'. The 'role' field was ignored.")
    else:
        flash(f"Welcome, {username}.")
    return redirect(url_for("dashboard"))

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

    # SECURE: escape user input instead of rendering as template
    if is_secure():
        rendered = str(escape(content))
    else:
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
    username = session.get("username")
    role = session.get("role")
    if not username:
        flash("Please log in first.")
        return redirect(url_for("index"))
    if role != "admin":
        flash("Access denied. Admin privileges required.")
        return redirect(url_for("dashboard"))

    name = request.args.get("name", "")

    if not name:
        # Show file listing
        available = []
        if os.path.isdir(FILES_DIR):
            available = os.listdir(FILES_DIR)
        return render_template("files.html", files=available, content=None)

    # SECURE: sanitize the filename to prevent directory traversal
    if is_secure():
        safe_name = os.path.basename(name)
        if safe_name != name:
            content = f"Access denied. Path traversal detected in '{name}'."
            return render_template("files.html", files=[], content=content,
                                   filename=name)
        name = safe_name

    # --- THE VULNERABILITY (in vulnerable mode) ---
    # The filename is concatenated directly without sanitization
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
    print("  Bypass -- Browser-Only Software Vulnerability CTF")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    print("  [!] This app is intentionally insecure.")
    print("  [!] For educational use only (CSCE A465).")
    print("=" * 60 + "\n")

    app.run(debug=True)
