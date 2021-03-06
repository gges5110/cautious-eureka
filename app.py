from flask import *
try:
    import credentials as credentials
except:
    pass
import os
import urllib
import requests
from flask_sqlalchemy import SQLAlchemy

# Routing setup
from views.api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.secret_key = os.environ.get('SECRET_KEY') if 'SECRET_KEY' in os.environ else credentials.app_secret_key

redirect_uri = ''
if os.environ['MODE'] == 'development':
    app.config.from_object('config.Config')
    redirect_uri = 'http://localhost:5000/callback'
elif os.environ['MODE'] == 'production':
    app.config.from_object('config.ProductionConfig')
    redirect_uri = 'https://cautious-eureka.herokuapp.com/callback'

db = SQLAlchemy(app)

# from models import Deck does not work...
from models import *
import db_init as db_init

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
                  client_id=os.environ.get('CLIENT_ID') if 'CLIENT_ID' in os.environ else credentials.client_id,
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
                    client_id=os.environ.get('CLIENT_ID') if 'CLIENT_ID' in os.environ else credentials.client_id,
                    client_secret=os.environ.get('CLIENT_SECRET') if 'CLIENT_SECRET' in os.environ else credentials.client_secret,
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

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/site-map")
def site_map():
    GET_links = []
    POST_links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            GET_links.append((url, rule.endpoint))

        if "POST" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            POST_links.append((url, rule.endpoint))

        template_values = {
            'GET_links': GET_links,
            'POST_links': POST_links
        }
    return render_template('site-map.html', **template_values)

if __name__ == '__main__':
    # https://stackoverflow.com/questions/17260338/deploying-flask-with-heroku
    # Bind to PORT if defined, otherwise default to 5000.
    db_init.init()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
