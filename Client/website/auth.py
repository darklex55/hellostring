from flask import Blueprint, make_response, render_template, request, redirect, url_for, flash
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
import requests
import json

auth = Blueprint('auth', __name__)

#Defines login route. After credentials are inserted, sents them to back end (Server) as a request. If the response is positive,
#user data are returned in the response and are inserted as a user cookie. The user is then redirected to homepage.
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if (current_user.is_authenticated):
        return redirect(url_for('views.home'))

    if (request.method=='POST'):
        email = request.form.get('e_mail')
        password = request.form.get('password')

        try:
            res = requests.get('http://127.0.0.1:8001/login_user', json=json.dumps({"email":email, "password": password}))
        except:
            flash('Error connecting to server', category='error')
            return render_template("login.html"), 400

        if res.status_code==200:
                res = res.json()
                print(res)
                login_user(User(res.get('id'),res.get('email'),res.get('password'),res.get('is_authed'),res.get('auth_key'),res.get('mail_auth_key'),res.get('is_privilleged')), remember=True)############
                return redirect(url_for('views.home'))
        else:
            print(res)
            flash('Incorrect login', category='error')

    return render_template("login.html")

#Defines logout route. Simply redirect user to login page after it deletes user's cookie.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfuly', category='success')
    return redirect(url_for('auth.login'))

#Defines sign up route. Sents credentials to back end (Server) as a request. If response is successful (200),
#sets the user cookie and redirects yser to homepage.
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    if (current_user.is_authenticated):
        return redirect(url_for('views.home'))

    if (request.method=='POST'):
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        e_mail = request.form.get('e_mail')

        try:
            res = requests.post('http://127.0.0.1:8001/register_user', json=json.dumps({"email":e_mail, "p1": password1, "p2": password2, "front_url": request.url_root }))
        except:
            flash('Error connecting to server', category='error')
            return render_template("sign_up.html"), 400

        if res.status_code==200:
            res = res.json()
            login_user(User(res.get('id'),res.get('email'),res.get('password'),res.get('is_authed'),res.get('auth_key'),res.get('mail_auth_key'), res.get('is_privilleged')), remember=True)
            flash('Account created!', category='success')
            #session.clear()
            return redirect(url_for('auth.login'))

        else:
            res = res.json()
            flash(res.get('reason'), category='error')


    resp = make_response(render_template("sign_up.html", error_username=False))

    return resp
