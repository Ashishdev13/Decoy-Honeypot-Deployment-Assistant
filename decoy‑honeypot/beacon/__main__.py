"""Allow running as: python -m beacon"""
from beacon.server import app

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Honeypot Beacon Server")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5001, help="Port (default: 5001)")
    args = parser.parse_args()

    print(f"[*] Beacon server starting on {args.host}:{args.port}")
    print("[!] WARNING: Use gunicorn for production (see wsgi.py)")
    app.run(host=args.host, port=args.port, debug=False)
