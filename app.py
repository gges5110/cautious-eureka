from flask import *
import credentials as credentials
import os
import urllib
import requests
from flask_sqlalchemy import SQLAlchemy

# Routing setup
from views.api import api

app = Flask(__name__)
app.register_blueprint(api)
app.secret_key = credentials.app_secret_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://sid:sid12345@localhost:5432/flash_cards'
db = SQLAlchemy(app)

# from models import Deck does not work...
from models import *

redirect_uri = 'http://localhost:5000/callback'
auth_uri = 'https://accounts.google.com/o/oauth2/auth'
token_uri = 'https://accounts.google.com/o/oauth2/token'
scope = ('https://www.googleapis.com/auth/userinfo.profile',
         'https://www.googleapis.com/auth/userinfo.email')
profile_uri = 'https://www.googleapis.com/oauth2/v1/userinfo'

@app.route('/')
@app.route('/index')
def index():
    userEmail = None
    profilePicURL = None
    if 'email' in session:
        userEmail = session['email']
    if 'profile_pic_url' in session:
        profilePicURL = session['profile_pic_url']

    template_values = {
        'email': userEmail,
        'profile_pic_url': profilePicURL
    }
    return render_template('index.html', **template_values)

@app.route('/logout')
def logout():
    session.pop('email', '')
    session.pop('profile_pic_url', '')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    # Step 1
    params = dict(response_type='code',
                  scope=' '.join(scope),
                  client_id=credentials.client_id,
                  approval_prompt='force',  # or 'auto'
                  redirect_uri=redirect_uri)
    #   https://stackoverflow.com/questions/28906859/module-has-no-attribute-urlencode
    url = auth_uri + '?' + urllib.parse.urlencode(params)
    return redirect(url)

@app.route('/callback', methods=['GET'])
def callback():
    if 'code' in request.args:
        # Step 2
        code = request.args.get('code')
        data = dict(code=code,
                    client_id=credentials.client_id,
                    client_secret=credentials.client_secret,
                    redirect_uri=redirect_uri,
                    grant_type='authorization_code')
        r = requests.post(token_uri, data=data)
        # Step 3
        access_token = r.json()['access_token']
        r = requests.get(profile_uri, params={'access_token': access_token})
        session['email'] = r.json()['email']
        session['profile_pic_url'] = r.json()['picture']


        if User.query.filter_by(user_email=session['email']).count() == 0:
            # Automatically create an account for user if not found in our database.
            new_user = User(user_email=session['email'])
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('index'))
    else:
        return 'ERROR'

if __name__ == '__main__':
    # https://stackoverflow.com/questions/17260338/deploying-flask-with-heroku
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
