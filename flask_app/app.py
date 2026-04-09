from flask import Flask, render_template, request

from db import get_connection
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
        connection = get_connection()
        cursor = connection.cursor()
        insert_query = "INSERT INTO users (first_name, last_name) VALUES (%s, %s)"
        cursor.execute(insert_query, (first_name, last_name))
        connection.commit()
        cursor.close()
        connection.close()
        return f"{first_name} {last_name} successfully inserted"
    return render_template('form_sync.html')


@app.route('/form_async', methods=['GET', 'POST'])
def take_data_async():
    if request.method == 'POST':
        first_name = request.form['fname']
        last_name = request.form['lname']
        task = insert_user.delay(first_name, last_name)
        return f"{first_name} {last_name} successfully inserted"
    return render_template('form_async.html')
