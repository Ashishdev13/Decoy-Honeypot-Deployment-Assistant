<div align="center">

# Decoy & Honeypot Deployment Assistant

**A Python toolkit for generating weaponized decoy documents with embedded tracking links and deploying a realistic Flask-based honeypot login page that captures attacker interactions.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Security](https://img.shields.io/badge/Honeypot-Deception-e94560?style=for-the-badge&logo=hackthebox&logoColor=white)](#)
[![Educational](https://img.shields.io/badge/Purpose-Educational-yellow?style=for-the-badge)](#%EF%B8%8F-disclaimer)

</div>

---

## About The Project

This tool enables security professionals to quickly deploy **low-interaction honeypots** using two components:

1. **Decoy Document Generator** — Creates realistic `.docx` files containing embedded hyperlinks that point to your beacon server. When a target (e.g., an attacker who has breached a network) opens the document and clicks the link, their interaction is silently logged.

2. **Beacon Server** — A Flask-based fake login page that looks like a legitimate corporate portal. It captures and logs all page views (IP, User-Agent) and credential submission attempts for threat intelligence analysis.

Together, these components form a **document-based deception strategy** — plant decoy files in sensitive-looking directories, and when an attacker interacts with them, you gain visibility into the intrusion.

### What This Tool Does

| Component | Functionality |
|-----------|--------------|
| **Beacon Server** | Serves a styled fake login page at `/login`, logs all visitor IPs, User-Agents, and submitted credentials |
| **Decoy Generator** | Creates `.docx` files with embedded tracking links that point to the beacon server |
| **Rate Limiter** | Built-in per-IP rate limiting (20 req/min) to prevent log flooding |
| **Log Rotation** | Automatic log file rotation (5MB max, 3 backups) to prevent disk exhaustion |
| **Security Headers** | Responses include CSP, X-Frame-Options, X-Content-Type-Options for realism |

---

## Demo

### Starting the Beacon Server
```
$ python -m beacon --host 127.0.0.1 --port 5001
[*] Beacon server starting on 127.0.0.1:5001
[!] WARNING: Use gunicorn for production (see wsgi.py)
 * Running on http://127.0.0.1:5001
```

### Generating a Decoy Document
```
$ python -m decoygen docx -u https://your-server.com/login -o bait.docx
Decoy written to /path/to/bait.docx
```

### Captured Log Output
```
2026-02-28 04:15:23 Page view from 192.168.1.50 - Mozilla/5.0 (Windows NT 10.0; Win64)
2026-02-28 04:15:31 Login attempt from 192.168.1.50 - Mozilla/5.0 (Windows NT 10.0) - user:admin
2026-02-28 04:15:45 Login attempt from 192.168.1.50 - Mozilla/5.0 (Windows NT 10.0) - user:root
2026-02-28 04:16:02 Rate limit exceeded for 192.168.1.50
```

### Fake Login Page
The beacon serves a clean, styled login page designed to look like a real corporate portal — complete with CSRF tokens and security headers for realism.

---

## Security Concepts Demonstrated

### Deception & Honeypot Techniques
- **Canary Documents** — Planting bait files that alert defenders when accessed by unauthorized users
- **Low-Interaction Honeypots** — Simulated services that log attacker behavior without exposing real systems
- **Credential Harvesting Detection** — Capturing what credentials attackers try reveals password patterns and reuse

### Defensive Security
- **Log Injection Prevention** — All user-controlled input (IP, User-Agent, form data) is sanitized before logging to prevent stored XSS via log poisoning
- **Input Validation** — URL scheme validation (http/https only) and path traversal prevention on file outputs
- **Rate Limiting** — Per-IP request throttling to prevent denial-of-service and log flooding attacks
- **Security Headers** — CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy applied to all responses
- **Log Rotation** — Bounded log files with `RotatingFileHandler` to prevent disk exhaustion attacks
- **CSRF Tokens** — Fake login form includes CSRF tokens for realism and to avoid easy fingerprinting

### Secure Development Practices
- **Metadata Stripping** — Generated documents have `python-docx` metadata removed to avoid revealing the tool used
- **Safe Defaults** — Server binds to `127.0.0.1` by default (not `0.0.0.0`), requires explicit flag for public binding
- **Production Readiness** — Includes `wsgi.py` for gunicorn deployment instead of relying on Flask's dev server
- **Error Handling** — Graceful error handling prevents raw tracebacks from leaking to users

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.8+** | Core language |
| **Flask 3.1** | Lightweight web framework for the beacon server |
| **Jinja2** | Template rendering with auto-escaping (XSS protection) |
| **MarkupSafe** | HTML entity escaping for log sanitization |
| **python-docx** | Word document generation for decoy files |
| **Click** | CLI framework for the document generator |
| **Gunicorn** | Production WSGI server (recommended for deployment) |
| **Werkzeug** | WSGI utilities and request handling |

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/Ashishdev13/Decoy-Honeypot-Deployment-Assistant.git
cd Decoy-Honeypot-Deployment-Assistant/decoy‑honeypot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Quick Verify
```bash
# Test the beacon server
python -m beacon --help

# Test the document generator
python -m decoygen docx --help
```

---

## Usage

### 1. Start the Beacon Server

```bash
# Development (localhost only)
python -m beacon --host 127.0.0.1 --port 5001

# Production (with gunicorn)
gunicorn wsgi:app --bind 127.0.0.1:5001 --workers 2

# Expose publicly (only with authorization)
python -m beacon --host 0.0.0.0 --port 5001
```

### 2. Generate a Decoy Document

```bash
# Basic usage
python -m decoygen docx -u https://your-server.com/login

# Custom output path
python -m decoygen docx -u https://your-server.com/login -o confidential-report.docx
```

### 3. Deploy the Decoy

- Place the generated `.docx` in sensitive-looking directories (`/share/finance/`, `C:\Backup\`)
- Name it something enticing (`employee-salaries-2026.docx`, `admin-credentials.docx`)
- Monitor `beacon.log` for attacker interactions

### 4. Monitor Logs

```bash
# Watch logs in real-time
tail -f beacon/beacon.log
```

### Deployment Options

| Method | Command | Use Case |
|--------|---------|----------|
| **Local** | `python -m beacon` | Testing and development |
| **Gunicorn** | `gunicorn wsgi:app --bind 0.0.0.0:5001` | Production deployment |
| **ngrok** | `ngrok http 5001` | Temporary public URL for testing |
| **AWS EB** | Deploy with `gunicorn` via Elastic Beanstalk | Cloud-hosted honeypot |

---

## Project Structure

```
Decoy-Honeypot-Deployment-Assistant/
└── decoy‑honeypot/
    ├── beacon/
    │   ├── __init__.py        # Package init
    │   ├── __main__.py        # Package entry point (python -m beacon)
    │   └── server.py          # Flask beacon server with security hardening
    ├── decoygen/
    │   ├── __init__.py        # Package init
    │   ├── __main__.py        # Package entry point (python -m decoygen)
    │   └── cli.py             # CLI document generator with input validation
    ├── wsgi.py                # Gunicorn WSGI entry point for production
    ├── requirements.txt       # Pinned dependencies
    └── .gitignore             # Excludes logs, caches, generated docs
```

---

## Disclaimer

> **This tool is developed strictly for educational purposes and authorized security testing.**

- This honeypot toolkit is designed for **security professionals, penetration testers, and students** learning about deception-based defense strategies.
- Deploy honeypots **only on networks and systems you own or have explicit written authorization to test on**.
- **Never use this tool to collect real credentials** from unsuspecting users. Honeypots should target attackers, not legitimate users.
- Deploying unauthorized honeypots or deceptive login pages may violate laws including the **Computer Fraud and Abuse Act (CFAA)**, **GDPR**, and similar legislation worldwide.
- The authors assume **no liability** for any misuse, damage, or legal consequences resulting from the use of this tool.
- Captured credentials should be treated as **sensitive data** — secure the log files and delete them when no longer needed.

**By using this tool, you agree that you are solely responsible for your actions and will only use it in authorized contexts.**

---

## License

Copyright &copy; 2025 Ashish Choudhary. All rights reserved.

---

<div align="center">
<sub>Built for learning deception-based defense and honeypot deployment strategies.</sub>
</div>
