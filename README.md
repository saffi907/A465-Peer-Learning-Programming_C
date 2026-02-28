# Bypass: A Browser-Only Software Vulnerability CTF

> A deliberately vulnerable Flask app for **CSCE A465 Computer & Network Security**.
> Every vulnerability is exploitable using only a web browser and free online tools.

> **WARNING:** This app is intentionally insecure.
> **DO NOT** run this on any public-facing server.

## Quick Start

```bash
pip install flask
python app.py
```

Open **http://127.0.0.1:5000** in your browser and you're good to go.

## How the Attack Chain Works

There are 4 stages. Each one builds on the last, you need info from the previous stage to pull off the next one.

### Stage 1: Poking Around (Info Disclosure)

1. Go to the login page at `http://127.0.0.1:5000`.
2. Open DevTools (F12) and check the **Sources** tab.
3. Open `app.js` - there's a comment a dev forgot to take out that mentions `/api/debug`.
4. Visit `http://127.0.0.1:5000/api/debug` in your browser.
5. The JSON response leaks a hidden endpoint: `/register`.

**What went wrong:** A debug endpoint got left in the code and it spills internal info to anyone who finds it.

### Stage 2: Getting Admin (Mass Assignment)

1. Go to the hidden registration page at `/register`.
2. Open DevTools (F12) and find the `<form>` in the Elements tab.
3. Add a hidden input inside the form: `<input name="role" value="admin">`.
4. Pick a username and password, then submit.
5. Log in with your new admin account.

**What went wrong:** The server just takes whatever fields you send it without checking which ones it should actually accept.

### Stage 3: Running Code on the Server (SSTI)

1. Go to the **Admin Panel** from the dashboard.
2. In the announcement box, type `{{ 7*7 }}` and submit.
3. If you see `49` in the output, that means that the server is running your template code.
4. Try `{{ config.items() }}` to dump the server config.
5. Look for `FLAG_PATH` and `FILES_ENDPOINT` in the output.

**What went wrong:** User input gets passed straight to `render_template_string()` with no escaping, so the server just runs whatever Jinja2 code you give it.

### Stage 4: Reading the Flag (Path Traversal)

1. Go to the file browser URL you found in Stage 3 (`/files`).
2. Notice the URL uses `?name=filename` to load files.
3. Change the URL to: `/files?name=../secret/flag.txt`
4. The server reads the flag file and shows you the contents.
5. Submit the flag to win.

**What went wrong:** The server just sticks user input into a file path with no sanitization, so you can use `../` to escape the intended directory.

## What Tools You Need

Literally just your browser:

- **DevTools Sources tab** - to read the JavaScript source
- **Browser URL bar** - to visit the debug endpoint and mess with URL params
- **DevTools Elements tab** - to add a hidden form field
- **A text input box** - to type Jinja2 template syntax

No Burp Suite, no curl, no terminal needed.

## Project Structure

```
.
|-- app.py                  # Flask server (all routes + vulns)
|-- secret/
|   +-- flag.txt            # The flag you're trying to get
|-- static/
|   |-- app.js              # has the debug endpoint hint
|   +-- style.css           # dark terminal theme
|-- templates/
|   |-- base.html           # shared layout
|   |-- login.html          # login page
|   |-- register.html       # hidden registration (Stage 2)
|   |-- dashboard.html      # user dashboard
|   |-- admin.html          # admin panel (Stage 3)
|   |-- files.html          # file browser (Stage 4)
|   +-- victory.html        # win screen with recap
+-- README.md
```

## Secure Mode (the Prevention Mechanism)

After you capture the flag, hit **Switch to Secure Mode** on the victory page. This resets your session and patches all 4 vulnerabilities on the server side. Try the same attacks again, they'll all fail now:

- **Stage 1:** `/api/debug` returns a 404 instead of leaking info
- **Stage 2:** The server ignores the extra `role` field and only takes username + password
- **Stage 3:** `{{ 7*7 }}` shows up as plain text instead of getting executed
- **Stage 4:** Path traversal with `../` gets caught and blocked

There's a red/green badge on every page so you can tell which mode you're in. You can toggle back to vulnerable mode from the login page via `/toggle-secure`.

## What You Should Take Away

1. **Don't leave debug stuff in production.** Remove dev-only routes and don't hardcode secrets.
2. **Only accept the fields you expect.** Don't just blindly take everything a form sends you.
3. **Don't pass user input to template engines.** Use `render_template()` with actual template files, not `render_template_string()`.
4. **Clean up file paths.** Use `os.path.basename()` or an allowlist so people can't escape the directory.

## Acknowledgments

Built for the CSCE A465 Peer Learning Activity at UAA.
AI tools (Google Gemini) were used to help build this.