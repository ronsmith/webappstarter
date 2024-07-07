import logging
import os

from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory, make_response
from dotenv import load_dotenv
from .dbsession import DBSessionInterface
from .db import DBPool

load_dotenv()

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.WARNING))
_logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = b'c61551d364ddd8d42775eb00796f501092b14d1378e60a6980c31e49ccffe80a'
app.db_pool = DBPool()
app.session_interface = DBSessionInterface()


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
        pass
    # else of fall-thru
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
