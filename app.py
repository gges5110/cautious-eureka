from flask import *

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', **locals())

if __name__ == '__main__':
    app.run(debug=True)
