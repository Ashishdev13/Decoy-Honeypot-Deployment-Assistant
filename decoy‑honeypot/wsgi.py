"""WSGI entry point for production deployment with gunicorn.

Usage:
    gunicorn wsgi:app --bind 127.0.0.1:5001 --workers 2
"""

from beacon.server import app

if __name__ == "__main__":
    app.run()
