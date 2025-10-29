import os
import json
import base64
from flask import Flask, redirect, url_for, session, jsonify, abort, request, send_from_directory, render_template
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)
# For local development help: allow cookies to be sent in cross-site requests if needed.
# In production you should use HTTPS and SESSION_COOKIE_SECURE=True.
app.config.update(
    SESSION_COOKIE_SAMESITE=None,
    SESSION_COOKIE_SECURE=False,
)

FB_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
FB_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
oauth = OAuth(app)
oauth.register(
    name='facebook',
    client_id=FB_CLIENT_ID,
    client_secret=FB_CLIENT_SECRET,
    access_token_url='https://graph.facebook.com/v10.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v10.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email'},
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login')
def api_login():
    redirect_uri = url_for('api_authorize', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/api/authorize')
def api_authorize():
    print('api_authorize: request.cookies =', dict(request.cookies))
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get('me?fields=id,name,email')
    profile = resp.json()
    session['user'] = {
        'id': profile.get('id'),
        'name': profile.get('name'),
        'email': profile.get('email')
    }
    session['token'] = token
    print('api_authorize: session after login =', dict(session))
      
    return redirect('http://localhost:5000/api/user')


@app.route('/api/user')
def api_user():

    user = session.get('user')
    if not user:
        return jsonify({'error': 'not_authenticated'}), 401
    return jsonify(user), 200


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    session.pop('token', None)
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(port=5000, debug=True)