from flask import Blueprint, flash, render_template, request, session, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user, logout_user
from urllib.parse import quote
import requests, json

views = Blueprint('views', __name__)

#Define home route. GET method requests history data from back end if user is a verified user. Every request to the backend
#is inside a try - except structure. This enables the front-end (Client) to run even if the back end (Server) is down.
#POST method redirects the user to the analyze route with the text entered (and the auth key if user is verified) as url parameters.
@views.route('/', methods=['GET','POST'])
def home():
    session.clear()
    old_records = []
    if request.method=='GET':
        if (current_user.is_authenticated):
            try:
                res = requests.get('http://127.0.0.1:8001/get_user_history', json=json.dumps({'auth_key': current_user.auth_key}))
                old_records = res.json().get('last_records')
            except:
                flash('Error connecting to server', category='error')


    if request.method=='POST':
        if len(request.form.get('summary'))>0:
            uid = ''
            if (current_user.is_authenticated):
                uid = current_user.auth_key
            return redirect(url_for('views.analyze', text = quote(request.form.get('summary')), auth = uid))
    return render_template("home.html", old_records = old_records, old_records_exist = len(old_records)>0), 200

#Defines analyze route. GET method requests the analysis from back end using as parameters the text (and the auth key if defined) from the user_id.
#Response is recieved as a json. Contains all the data from analysis done in the back end. Data is directly served in the page's template.
@views.route('/analyze', methods=['GET'])
def analyze():
    session.clear()
    if ('text' in request.args):
        inserted_text = request.args.get('text')
        is_authed = False
        if current_user.is_authenticated:
            if current_user.is_authed:
                is_authed = True

        try:
            if ('auth' in request.args):
                res = requests.get('http://127.0.0.1:8001/analyze_front', json=json.dumps({"inserted_text": inserted_text, "is_authed": is_authed, 'auth': request.args.get('auth')}))
            else:
                res = requests.get('http://127.0.0.1:8001/analyze_front', json=json.dumps({"inserted_text": inserted_text, "is_authed": is_authed}))
        except:
            flash('Error connecting to server', category='error')
            return render_template("home.html"), 400

        if (res.status_code==200):
            res = res.json()
            return render_template("analyze.html",
            inserted_text = res.get('pos'),
            char_count = res.get('len'),
            word_count = res.get('tokens_word'),
            sent_count = res.get('tokens_sent'),
            punc_count = res.get('punkt'),
            chart_tokens = ['a','b','c'],
            chart_values = [5,3,1],
            wfi = res.get('freq_anal'),
            sentiment_score = res.get('sentiment_anal'),
            aggressiveness_score = res.get('sentiment_aggr'),
            is_authed = is_authed), 200
        else:
            return make_response(jsonify({'error': 'Server side error'}), 400)

    else:
        return make_response(jsonify({'error': 'No text argument'}), 400)

#User settings route. POST method #1 sents request to back end (Server) with user data, in order to delete user.
#On success, logs out the user. POST method #2 sents request to back end server with front-end's endpoint and user's id as parameters.
#On success, back end (Server) resends the verification email to specific user.
@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    session.clear()
    if request.method=='POST' and request.form['btn'] == 'Delete':
        try:
            res = requests.post('http://127.0.0.1:8001/delete_user', json=json.dumps({"user_id":current_user.id}))
        except:
            flash('Error connecting to server', category='error')
            return render_template("settings.html"), 400
        if (res.status_code==200):
            flash('User deleted successfuly', category='success')
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash('Error deleting user', category='error')
            return redirect(url_for('views.settings'))

    if request.method=='POST' and request.form['btn'] == 'Resend':
        try:
            res = requests.post('http://127.0.0.1:8001/resend_verification', json=json.dumps({"user_id":current_user.id, "front_url": request.url_root}))
        except:
            flash('Error connecting to server', category='error')
            return render_template("settings.html"), 400

        if (res.status_code==200):
            flash('Verification email sent to ' + current_user.email, category='success')
        else:
            flash('Error resending email. Please try again later.', category='error')
    return render_template("settings.html", user_email=current_user.email, is_authed = current_user.is_authed, auth_key = current_user.auth_key)

#API docs route. Sents a simple, static page to user.
@views.route('/api_docs')
def api_docs():
    session.clear()
    return render_template("api.html"), 200

#Monitor route. On load, requests verified users list from back-end. The users are passed to the page's template. On that template,
#a js script is defined to dynamically fetch history data from backend when selecting a user email.
@views.route('/monitor')
@login_required
def monitor():
    if (current_user.is_privilleged):
        user_emails = []
        try:
            res = requests.get('http://127.0.0.1:8001/get_registered_users?auth=' + current_user.auth_key)
            if (res.status_code==200):
                user_emails = res.json().get('emails')
        except:
            flash('Error connecting to server', category='error')

        session.clear()
        return render_template("monitor.html", user_emails = user_emails), 200
    else:
        session.clear()
        flash('No privilleges to access this page', 'error')
        return render_template("home.html"), 200

#Verification route. Sents request to back-end (Server) with mail's authentication key (provided from URI's parameters) when a users
#clicks the verification link from his email. Redirects user to homepage and informs them with a flash message for the outcome.
@views.route('/verification')
def account_verification():
    session.clear()
    if 'auth_key' in request.args:
        try:
            res = requests.post('http://127.0.0.1:8001/verify_user', json=json.dumps({"auth_key":request.args['auth_key']}))
        except:
            flash('Error connecting to server', category='error')
            return render_template("home.html"), 400

        if (res.status_code==200):
            flash('Verification Completed Successfuly', category='success')
        else:
            flash('Verification Error', category='error')

    else:
        flash('Verification Error', category='error')
    return render_template("home.html"), 200
