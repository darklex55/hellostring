from flask import Blueprint, make_response, render_template, request, redirect, url_for, flash
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from website.python_utils import produceHashFromText, sendValidationEmail;

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if (current_user.is_authenticated):
        return redirect(url_for('views.home'))

    if (request.method=='POST'):
        email = request.form.get('e_mail')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            if check_password_hash(user.password, password):
                user.last_login = datetime.today()
                db.session.commit()
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else: 
                flash('Incorrect login', category='error')
        else: 
            flash('Incorrect login', category='error')


    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfuly', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    if (current_user.is_authenticated):
        return redirect(url_for('views.home'))

    if (request.method=='POST'):
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        e_mail = request.form.get('e_mail')
        stored_email = User.query.filter_by(email=e_mail).first()

        if password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters.', category='error')
        elif stored_email:
            flash('E-mail is already in use.', category='error')
        else:
            new_user = User(email=e_mail, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            user = User.query.filter_by(email=e_mail).first()
            user.mail_auth_key = produceHashFromText(str(user.id))
            db.session.commit()

            sendValidationEmail(e_mail, produceHashFromText(str(user.id)), request.url_root)

            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            #session.clear()
            return redirect(url_for('auth.login'))


    resp = make_response(render_template("sign_up.html", error_username=False))

    return resp