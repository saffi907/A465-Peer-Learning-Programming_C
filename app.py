# app.py -- CryptoChain: Browser-Only Cryptography CTF
# ============================================================================
# EDUCATIONAL DEMO ONLY:
# This application intentionally demonstrates common security anti-patterns
# in a controlled localhost environment for CSCE A465.
#
# DO NOT deploy this application on any network-accessible host.
# ============================================================================

import base64
import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, make_response, flash
)

app = Flask(__name__)
app.secret_key = "dev-key-not-for-production"

# ---------------------------------------------------------------------------
# Hardcoded users (no database needed)
# ---------------------------------------------------------------------------
USERS = {
    "agent":   {"password": "shadow42", "role": "user"},
    "admin":   {"password": "override9", "role": "admin"},
}

# The "secret credentials" hidden as a Base64 comment in login.html
# agent:shadow42  -->  base64 = YWdlbnQ6c2hhZG93NDI=
HIDDEN_CREDS_B64 = base64.b64encode(b"agent:shadow42").decode()

# Caesar cipher clue (shift = 3) for the hidden vault path
# Plaintext: "the hidden vault is at /vault/secret-stash"
# Each letter shifted +3 in the alphabet
CAESAR_PLAINTEXT = "the hidden vault is at /vault/secret-stash"

def caesar_encrypt(text, shift=3):
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('a') if ch.islower() else ord('A')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)

CAESAR_CIPHERTEXT = caesar_encrypt(CAESAR_PLAINTEXT, 3)

# Hex-encoded flag for the vault
FLAG_TEXT = "FLAG{cr4ck_th3_c0d3_A465}"
FLAG_HEX = FLAG_TEXT.encode().hex()


# ---------------------------------------------------------------------------
# Route: Login Page
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("login.html", hidden_b64=HIDDEN_CREDS_B64)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    user = USERS.get(username)
    if user and user["password"] == password:
        # VULNERABILITY: role is stored in a plaintext cookie
        # The client can freely edit it in DevTools.
        resp = make_response(redirect(url_for("dashboard")))
        resp.set_cookie("username", username)
        resp.set_cookie("role", user["role"])      # <-- the vuln
        return resp
    else:
        flash("Invalid credentials. Try harder.")
        return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Route: User Dashboard
# ---------------------------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    username = request.cookies.get("username")
    role     = request.cookies.get("role")

    if not username:
        flash("Please log in first.")
        return redirect(url_for("index"))

    return render_template("dashboard.html", username=username, role=role)


# ---------------------------------------------------------------------------
# Route: Admin Panel
# VULNERABILITY: access control relies on the plaintext cookie value.
# ---------------------------------------------------------------------------
@app.route("/admin")
def admin_panel():
    role = request.cookies.get("role")

    if role != "admin":
        flash("Access denied. Admin privileges required.")
        return redirect(url_for("dashboard"))

    return render_template(
        "admin.html",
        caesar_cipher=CAESAR_CIPHERTEXT,
    )


# ---------------------------------------------------------------------------
# Route: The Vault (hidden endpoint discovered via Caesar cipher)
# VULNERABILITY: security through obscurity -- the URL is the only
# "protection." Anyone who knows the path can access it.
# ---------------------------------------------------------------------------
@app.route("/vault/secret-stash")
def vault():
    return render_template("vault.html", flag_hex=FLAG_HEX)


@app.route("/vault/check-flag", methods=["POST"])
def check_flag():
    submitted = request.form.get("flag", "").strip()
    if submitted == FLAG_TEXT:
        return render_template("victory.html", flag=FLAG_TEXT)
    else:
        flash("Incorrect flag. Decode the hex string and try again.")
        return redirect(url_for("vault"))


# ---------------------------------------------------------------------------
# Route: Logout
# ---------------------------------------------------------------------------
@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("username")
    resp.delete_cookie("role")
    return resp


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  CryptoChain -- Browser-Only Cryptography CTF")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    print("  [!] This app is intentionally insecure.")
    print("  [!] For educational use only (CSCE A465).")
    print("=" * 60)
    print()
    app.run(host="127.0.0.1", port=5000, debug=True)
