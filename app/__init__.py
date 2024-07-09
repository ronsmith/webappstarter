import logging
import os

from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory, make_response, flash
from dotenv import load_dotenv

from .remember import get_remember_me, set_remember_me
from .dbsession import DBSessionInterface
from .db import DBPool
from .user import login_user

load_dotenv()

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.WARNING))
_logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = b'c61551d364ddd8d42775eb00796f501092b14d1378e60a6980c31e49ccffe80a'
app.db_pool = DBPool()
app.session_interface = DBSessionInterface(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = user.login(app.db_pool.getconn(), request.form['email'], request.form['password'])
        if u:
            resp = make_response(redirect(url_for(request.args.get('next', 'index'))))
            session.userid = u.id
            set_remember_me(request, resp)

        else:
            flash('Invalid email or password', category='error')

    # else fall-thru
    return render_template('login.html', remember=get_remember_me(request))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
