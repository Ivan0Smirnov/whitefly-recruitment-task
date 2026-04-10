from flask import Flask, render_template, request

from db import get_connection, run_query
from tasks import insert_user

app = Flask(__name__)


@app.route("/")
def hello_world():
    return '<p>Hello, World!</p>'


@app.route('/form_sync', methods=['GET', 'POST'])
def take_data_sync():
    if request.method == 'POST':
        first_name = request.form['fname']
        last_name = request.form['lname']
        run_query("INSERT INTO users (first_name, last_name) VALUES (%s, %s)", (first_name, last_name))
        return f"{first_name} {last_name} successfully inserted"
    return render_template('form_sync.html')


@app.route('/form_async', methods=['GET', 'POST'])
def take_data_async():
    if request.method == 'POST':
        first_name = request.form['fname']
        last_name = request.form['lname']
        insert_user.delay(first_name, last_name)
        return f"{first_name} {last_name} successfully inserted"
    return render_template('form_async.html')
