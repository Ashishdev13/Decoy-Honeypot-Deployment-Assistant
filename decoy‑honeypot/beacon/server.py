#!/usr/bin/env python3
"""Flask beacon server — serves a fake login page and logs interactions."""

import os
import re
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, redirect, render_template_string
from markupsafe import escape

app = Flask(__name__)

# --- Logging with rotation and sanitization ---

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "beacon.log")

handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))

logger = logging.getLogger("beacon")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def sanitize_log(value):
    """Strip control characters and HTML to prevent log injection."""
    value = str(value) if value else ""
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)  # strip control chars
    value = str(escape(value))  # escape HTML entities
    return value[:500]  # truncate to prevent log flooding


# --- Security headers middleware ---

@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# --- Rate limiting ---

_request_counts = {}
RATE_LIMIT = 20  # max requests per IP per minute
RATE_WINDOW = 60  # seconds


def _check_rate_limit(ip):
    """Simple in-memory rate limiter. Returns True if rate exceeded."""
    import time
    now = time.time()
    if ip not in _request_counts:
        _request_counts[ip] = []
    # Prune old entries
    _request_counts[ip] = [t for t in _request_counts[ip] if now - t < RATE_WINDOW]
    if len(_request_counts[ip]) >= RATE_LIMIT:
        return True
    _request_counts[ip].append(now)
    return False


# --- HTML template with CSRF token simulation ---

LOGIN_TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Secure Portal Login</title>
  <style>
    body { font-family: Arial, sans-serif; display: flex; justify-content: center;
           align-items: center; height: 100vh; margin: 0; background: #f4f4f4; }
    .login-box { background: white; padding: 30px; border-radius: 8px;
                 box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 320px; }
    h2 { margin-top: 0; color: #333; }
    label { display: block; margin: 10px 0 5px; color: #555; }
    input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;
            box-sizing: border-box; }
    button { width: 100%; padding: 10px; margin-top: 15px; background: #0066cc;
             color: white; border: none; border-radius: 4px; cursor: pointer; }
    button:hover { background: #0052a3; }
  </style>
</head>
<body>
  <div class="login-box">
    <h2>Secure Portal Login</h2>
    <form method="post" action="/login">
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}"/>
      <label>Username<input type="text" name="username" required/></label>
      <label>Password<input type="password" name="password" required/></label>
      <button type="submit">Login</button>
    </form>
  </div>
</body>
</html>'''


# --- Routes ---

@app.route("/beacon")
def beacon_redirect():
    return redirect("/login", code=302)


@app.route("/login", methods=["GET", "POST"])
def login():
    ip = sanitize_log(request.remote_addr)
    ua = sanitize_log(request.headers.get("User-Agent", ""))

    if _check_rate_limit(request.remote_addr):
        logger.warning(f"Rate limit exceeded for {ip}")
        return ("<h3>Too many requests. Please try again later.</h3>", 429)

    try:
        if request.method == "GET":
            logger.info(f"Page view from {ip} - {ua}")
            # Generate a simple CSRF token for realism
            import secrets
            token = secrets.token_hex(16)
            return render_template_string(LOGIN_TEMPLATE, csrf_token=token)
        else:
            username = sanitize_log(request.form.get("username", ""))
            password = sanitize_log(request.form.get("password", ""))
            logger.info(f"Login attempt from {ip} - {ua} - user:{username}")
            return ("<h3>Invalid credentials. Please try again later.</h3>", 401)
    except Exception as e:
        logger.error(f"Error handling request from {ip}: {sanitize_log(str(e))}")
        return ("<h3>An error occurred.</h3>", 500)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Honeypot Beacon Server")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Bind address (default: 127.0.0.1, use 0.0.0.0 for all interfaces)")
    parser.add_argument("--port", type=int, default=5001, help="Port (default: 5001)")
    args = parser.parse_args()

    print(f"[*] Beacon server starting on {args.host}:{args.port}")
    print("[!] WARNING: Use gunicorn for production (see wsgi.py)")
    app.run(host=args.host, port=args.port, debug=False)
