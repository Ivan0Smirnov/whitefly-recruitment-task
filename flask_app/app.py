from flask import Flask, render_template, request

from db import run_query
from security import check_fingerprint, verify_recaptcha
from tasks import insert_user

app = Flask(__name__)


@app.route("/")
def hello_world():
    return '<p>Hello, World!</p>'


@app.route('/form_sync', methods=['GET', 'POST'])
def take_data_sync():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        bot_detection = request.form.get('website')
        fingerprint = request.form.get('fingerprint')
        captcha = request.form.get('g-recaptcha-response')

        if bot_detection:
            return "Error: Bot detected", 400
        if not verify_recaptcha(captcha):
            return "Error: Invalid CAPTCHA", 400
        if fingerprint and not check_fingerprint(fingerprint):
            return "Error: Too many submissions from this device, are you a bot?", 429

        run_query("INSERT INTO users (first_name, last_name, fingerprint_js) VALUES (%s, %s, %s)",
                  (first_name, last_name, fingerprint))
        return f"{first_name} {last_name} successfully inserted", 200
    return render_template('form_sync.html')


@app.route('/form_async', methods=['GET', 'POST'])
def take_data_async():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        bot_detection = request.form.get('website')
        fingerprint = request.form.get('fingerprint')
        captcha = request.form.get('g-recaptcha-response')

        if bot_detection:
            return "Error: Bot detected", 400
        if not verify_recaptcha(captcha):
            return "Error: Invalid CAPTCHA", 400
        if fingerprint and not check_fingerprint(fingerprint):
            return "Error: Too many submissions from this device, are you a bot?", 429

        insert_user.delay(first_name, last_name, fingerprint)
        return f"{first_name} {last_name} queued for insertion", 200
    return render_template('form_async.html')
