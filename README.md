# Bypass -- Browser-Only Software Vulnerability CTF

> A deliberately vulnerable Flask app for **CSCE A465 -- Computer & Network Security**.
> Every vulnerability is exploitable using only a web browser and free online tools.

> **WARNING:** This application is intentionally insecure.
> **DO NOT** deploy this application on any network-accessible host.

## Quick Start

```bash
pip install flask
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Attack Chain

```
+-------------------+     +-------------------+     +--------------------+     +------------------+
| 1. RECON          |---->| 2. ESCALATE       |---->| 3. INJECT          |---->| 4. EXFILTRATE    |
|                   |     |                   |     |                    |     |                  |
| JS source reveals |     | Mass assignment   |     | Server-Side        |     | Path traversal   |
| debug endpoint    |     | adds role=admin   |     | Template Injection |     | reads flag file  |
+-------------------+     +-------------------+     +--------------------+     +------------------+
```

### Stage 1: Information Disclosure

1. Open the login page at `http://127.0.0.1:5000`.
2. Open DevTools (F12) and go to the **Sources** tab.
3. Open `app.js` and find the comment revealing `/api/debug`.
4. Visit `http://127.0.0.1:5000/api/debug` in your browser.
5. The JSON response leaks a hidden endpoint: `/register`.

**Vulnerability:** Debug/development endpoints left in production code.

### Stage 2: Mass Assignment

1. Visit the hidden registration page at `/register`.
2. Open DevTools (F12) and find the `<form>` in the Elements tab.
3. Add a hidden input: `<input name="role" value="admin">` inside the form.
4. Fill in a username and password, then submit.
5. Log in with your new admin account.

**Vulnerability:** The server blindly accepts all form fields without validating which ones are allowed.

### Stage 3: Server-Side Template Injection (SSTI)

1. Navigate to the **Admin Panel** from the dashboard.
2. In the announcement box, type `{{ 7*7 }}` and submit.
3. If you see `49` in the rendered output, the server is executing your template code.
4. Type `{{ config.items() }}` to dump the server's configuration.
5. Look for `FLAG_PATH` and `FILES_ENDPOINT` in the output.

**Vulnerability:** User input passed directly to `render_template_string()` without sanitization.

### Stage 4: Path Traversal

1. Go to the file browser URL you found in Stage 3 (`/files`).
2. Notice the URL uses `?name=filename` to load files.
3. Change the URL to: `/files?name=../secret/flag.txt`
4. The server reads the flag file and displays its contents.
5. Submit the flag to win.

**Vulnerability:** File paths constructed from user input without sanitization, allowing `../` traversal.

## Tools Used

| Stage | Tool | Purpose |
|-------|------|---------|
| 1 | DevTools (Sources tab) | Read JavaScript source code |
| 1 | Browser URL bar | Visit the debug API endpoint |
| 2 | DevTools (Elements tab) | Add a hidden form field |
| 3 | Browser text input | Inject Jinja2 template syntax |
| 4 | Browser URL bar | Modify the `?name=` parameter |

## Project Structure

```
.
|-- app.py                  # Flask server (all routes + vulnerabilities)
|-- secret/
|   +-- flag.txt            # The flag to capture
|-- static/
|   |-- app.js              # Stage 1: contains debug endpoint hint
|   +-- style.css           # Dark terminal theme
|-- templates/
|   |-- base.html           # Shared layout
|   |-- login.html          # Login page (Stage 1 hint)
|   |-- register.html       # Hidden registration (Stage 2)
|   |-- dashboard.html      # User dashboard
|   |-- admin.html          # Admin panel (Stage 3 SSTI)
|   |-- files.html          # File browser (Stage 4)
|   +-- victory.html        # Win screen with recap
+-- README.md
```

## Key Takeaways

1. **Never leave debug endpoints in production.** Remove all development-only routes and use environment variables for configuration.
2. **Whitelist accepted input fields.** Never blindly accept all client-submitted form data. Explicitly extract only the fields you expect.
3. **Never pass user input to template engines.** Use `render_template()` with separate template files instead of `render_template_string()`.
4. **Sanitize all file paths.** Use `os.path.basename()` or an allowlist to prevent directory traversal attacks.

## Acknowledgments

This project was developed for the CSCE A465 Peer Learning Activity at UAA.
AI tools (Google Gemini) were used to assist in the development of this application.
