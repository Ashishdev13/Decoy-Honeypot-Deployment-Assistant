# Decoy & Honeypot Deployment Assistant

## Overview

A lightweight Python tool for generating decoy Word documents with embedded tracking links and deploying a simple Flask-based beacon server that serves a fake login page. Ideal for quick, low-interaction honeypot setups and document-based deception.

## Features

- **Decoy Document Generation:** Create `.docx` files with clickable links to your beacon.
- **Flask Beacon Server:** Serves a fake login at `/login`, redirects `/beacon` to `/login`, and logs page views and credential submissions in `beacon.log`.
- **Simple CLI:** Single-command decoy creation with customizable output path and target URL.

## Installation

```bash
git clone <repo_url>
cd decoy-honeypot
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

1. **Start the server**
   ```bash
   source .venv/bin/activate
   python -m beacon.server
   ```
2. **Generate a decoy**
   ```bash
   python -m decoygen.cli docx -u http://127.0.0.1:5001/login
   ```
3. **Open ********`decoy.docx`******** and click “Open portal login”**
4. \*\*Check \*\***`beacon.log`** for captured hits and credentials.

## Deployment Options

- **ngrok:** `ngrok http 5001` for temporary public URL
- **AWS EB:** Deploy via Elastic Beanstalk with `gunicorn`

## Directory Structure

```
decoy-honeypot/
├── decoygen/      # CLI generator code
├── beacon/        # Flask server code
├── .venv/         # Python virtualenv
└── requirements.txt
```

## License

Copyright © 2025 Ashish Choudhary. All rights reserved.

