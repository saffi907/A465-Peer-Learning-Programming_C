# CryptoChain -- Browser-Only Multi-Stage Cryptography CTF

> A deliberately vulnerable Flask app for **CSCE A465 -- Computer & Network Security**.
> Every vulnerability is exploitable using only a web browser and free online tools.
>
> **DO NOT** deploy this application on any network-accessible host.

---

## Quick Start

```bash
cd new
pip install flask
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Attack Chain Walkthrough

```
+-----------------+     +------------------+     +-------------------+     +-----------------+
| 1. RECON        |---->| 2. ESCALATE      |---->| 3. DECRYPT        |---->| 4. CAPTURE      |
|                 |     |                  |     |                   |     |                 |
| HTML comment    |     | Cookie tamper    |     | Caesar cipher     |     | Hex-to-ASCII    |
| + Base64 decode |     | role=user->admin |     | reveals hidden URL|     | decode the flag  |
+-----------------+     +------------------+     +-------------------+     +-----------------+
```

### Stage 1 -- Information Disclosure (Base64)

1. Open **http://127.0.0.1:5000** in your browser
2. Right-click anywhere on the login page, select **View Page Source**
3. Near the top, find the HTML comment containing a Base64 string
4. Copy the string and decode it at [base64decode.org](https://www.base64decode.org/)
5. It reveals `username:password` -- use these to log in

**Vulnerability:** Sensitive credentials left in HTML comments.
**Fix:** Strip all comments and debug data from production code.

### Stage 2 -- Broken Access Control (Cookie Tampering)

1. After logging in, you land on the User Dashboard with `role: user`
2. Open **DevTools** (F12) and go to **Application** > **Cookies**
3. Find the `role` cookie (currently set to `user`)
4. Change its value to `admin`
5. Refresh the page -- you now have admin access

**Vulnerability:** Authorization based on a client-controlled plaintext cookie.
**Fix:** Use server-side sessions or cryptographically signed tokens.

### Stage 3 -- Security Through Obscurity (Caesar Cipher)

1. Click **Enter Admin Panel** (or navigate to `/admin`)
2. In the System Log, find the highlighted `SECRET` entry
3. The text is encrypted with a Caesar cipher (shift = 3)
4. Decode it at [dcode.fr/caesar-cipher](https://www.dcode.fr/caesar-cipher)
5. The plaintext reveals a hidden URL path -- navigate to it

**Vulnerability:** Sensitive endpoints "protected" only by obscure URLs.
**Fix:** Enforce authentication and authorization on every endpoint.

### Stage 4 -- Weak Encoding (Hex to ASCII)

1. On the Vault page, you see a hex-encoded string
2. Copy the hex and decode it at [rapidtables.com/hex-to-ascii](https://www.rapidtables.com/convert/number/hex-to-ascii.html)
3. Enter the decoded flag in the input field
4. Submit to complete the CTF

**Vulnerability:** Sensitive data "encrypted" with reversible encoding.
**Fix:** Use real encryption (AES-256). Encoding (Base64, Hex) is not encryption.

---

## Tools Used (All Free, All Browser-Based)

| Tool | URL | Used For |
|------|-----|----------|
| Base64 Decoder | base64decode.org | Stage 1 |
| Browser DevTools | Built into Chrome/Firefox | Stage 2 |
| Caesar Cipher Decoder | dcode.fr/caesar-cipher | Stage 3 |
| Hex to ASCII | rapidtables.com/hex-to-ascii | Stage 4 |

---

## Project Structure

```
new/
  app.py             <-- Single Flask server (~140 lines)
  README.md          <-- You are here
  templates/
    base.html        <-- Shared layout (dark theme)
    login.html       <-- Login page (Base64 in HTML comment)
    dashboard.html   <-- User dashboard (cookie tampering)
    admin.html       <-- Admin panel (Caesar cipher clue)
    vault.html       <-- Vault (hex-encoded flag)
    victory.html     <-- Victory screen + recap
  static/
    style.css        <-- Dark terminal theme
```

---

## Key Takeaways

1. **Never store sensitive data in client-accessible locations.**
   HTML comments, JavaScript variables, and cookies are all readable by the user.

2. **Authorization must be enforced server-side.**
   Client-side cookies and tokens are attacker-controlled. Always verify on the server.

3. **Obscurity is not security.**
   Hidden URLs and weak ciphers do not protect endpoints. Use proper access controls.

4. **Encoding is not encryption.**
   Base64, hex, and similar encodings are trivially reversible. Use AES or similar for real protection.

---

## License

This project is for **educational purposes only** as part of CSCE A465
(Computer & Network Security) at the University of Alaska Anchorage.
