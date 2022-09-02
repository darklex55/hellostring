from flask import Blueprint, flash, render_template, request, session, redirect, url_for, jsonify, make_response
from website.python_utils import analysis_sentiment_analyzer, checkUserForAuth, produceHashFromText, sendValidationEmail, sentiment_analyzer, tokenizeSentence, tokenizeWords, wordFreq, remStopwords, stemmer, lemmatizer, pos_tagger, checkAuthToken, aggressiveness_analyzer, getPunctuationCount, posWordsAnalysis, wordFreqAnalysis, analysis_aggressiveness_analyzer
from flask_login import login_required, current_user, logout_user
from .models import User
from . import db
from urllib.parse import unquote, quote

views = Blueprint('views', __name__)

@views.route('/', methods=['GET','POST'])
def home():
    session.clear()
    if request.method=='POST':
        if len(request.form.get('summary'))>0:
            return redirect(url_for('views.analyze', text = quote(request.form.get('summary'))))
    return render_template("home.html"), 200

@views.route('/analyze', methods=['GET'])
def analyze():
    session.clear()
    if ('text' in request.args):
        inserted_text = unquote(request.args.get('text'))
        return render_template("analyze.html", 
        inserted_text = posWordsAnalysis(inserted_text), 
        char_count = len(inserted_text), 
        word_count = len(tokenizeWords(inserted_text)), 
        sent_count = len(tokenizeSentence(inserted_text)), 
        punc_count = getPunctuationCount(inserted_text),
        chart_tokens = ['a','b','c'],
        chart_values = [5,3,1],
        wfi = wordFreqAnalysis(request.args.get('text')),
        sentiment_score = analysis_sentiment_analyzer(request.args.get('text')),
        aggressiveness_score = analysis_aggressiveness_analyzer(request.args.get('text')),
        is_authed = checkUserForAuth()), 200

    else:
        return make_response(jsonify({'error': 'No text argument'}), 400)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    session.clear()
    if request.method=='POST' and request.form['btn'] == 'Delete':
        db.session.delete(current_user)
        db.session.commit()
        flash('User deleted successfuly', category='success')
        logout_user()
        return redirect(url_for('auth.login'))
    if request.method=='POST' and request.form['btn'] == 'Resend':
        sendValidationEmail(current_user.email, current_user.mail_auth_key, request.url_root)
        flash('Verification email sent to ' + current_user.email, category='success')
    return render_template("settings.html", user_email=current_user.email, is_authed = current_user.is_authed, auth_key = current_user.auth_key)


@views.route('/api_docs')
def api_docs():
    session.clear()
    return render_template("api.html"), 200

@views.route('/verification')
def account_verification():
    session.clear()
    if 'auth_key' in request.args:
        user = User.query.filter_by(mail_auth_key=request.args['auth_key']).first()

        if user:
            user.is_authed = True
            user.auth_key = produceHashFromText(str(user.email) + str(user.password))
            db.session.commit()
            flash('Verification Completed Successfuly', category='success')
        else:
            flash('Verification Error', category='error')

    else:
        flash('Verification Error', category='error')
    return render_template("home.html"), 200

@views.route('/api/tokenize', methods=['GET'])
def tokenize():
    if 'text' in request.args:
        return make_response(jsonify({'sentence_tokens': tokenizeSentence(request.args.get('text')), 'word_tokens': tokenizeWords(request.args.get('text'))}), 200)
    else:
        return make_response("No text argument", 400)

@views.route('/api/frequency', methods=['GET'])
def frequency():
    if 'text' in request.args:
        if 'level' in request.args:
            if request.args.get('level') in ['char','word']:
                return make_response(jsonify({'word_frequency': wordFreq(request.args.get('text'), request.args.get('level'))}), 200)
            else:
                return make_response('Argument "level incorrect', 400)
        else:
            return make_response(jsonify({'word_frequency': wordFreq(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/stopwords', methods=['GET'])
def stopwrds():
    if 'text' in request.args:
        tokens = False
        sw = []
        if 'tokens' in request.args:
            if unquote(request.args.get('tokens')) in ['yes','no']:
                tokens = True if request.args.get('tokens')=='yes' else False
            else:
                return make_response('Argument "tokens" incorrect', 400)

        if 'sw_list' in request.args:
            sw = request.args.get('sw_list')

        return make_response(jsonify({'stopwords': remStopwords(request.args.get('text'), sw = sw, tokens=tokens)}), 200)

    else:
        return make_response('No text argument', 400)

@views.route('/api/stemming', methods=['GET'])
def stem():
    if 'text' in request.args:
        if 'stemmer' in request.args:
            if request.args.get('stemmer') in ['porter','snowball']:
                return make_response(jsonify({'stemmed_string': stemmer(request.args.get('text'), request.args.get('stemmer'))}), 200)
            else:
                return make_response('Argument "stemmer" incorrect', 400)
        else:
            return make_response(jsonify({'stemmed_string': stemmer(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/lemmatization', methods=['GET'])
def lemmatize():
    if 'text' in request.args:
        return make_response(jsonify({'lemmatized_string': lemmatizer(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/pos', methods=['GET'])
def pos_tagging():
    if 'text' in request.args:
        return make_response(jsonify({'pos_tags': pos_tagger(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/sentiment', methods=['GET'])
def sentimentize():
    continuous = 'yes'
    method = 'vader'
    if 'auth' in request.args:
        if (not checkAuthToken(request.args.get('auth'))):
            return make_response('Invalid authenitcation', 401)
    else:
        return make_response('Invalid authenitcation', 401)

    if 'text' not in request.args:
         return make_response('No text argument', 400)
    
    if 'method' in request.args:
        if request.args.get('method') not in ['vader', 'textblob']:
            return make_response('Argument "method" incorrect', 400)
        method = request.args.get('method')


    if 'cont' in request.args:
        if request.args.get('cont') not in ['yes', 'no']:
            return make_response('Argument "cont" incorrect', 400)
        continuous = request.args.get('cont')

    
    return make_response(jsonify({'sentiment': sentiment_analyzer(text = request.args.get('text'), method = method, continuous=continuous)}), 200)

@views.route('/api/aggressiveness', methods=['GET'])
def aggressiveness():
    continuous = 'yes'
    if 'auth' in request.args:
        if (not checkAuthToken(request.args.get('auth'))):
            return make_response('Invalid authenitcation', 401)
    else:
        return make_response('Invalid authenitcation', 401)

    if 'cont' in request.args:
        if request.args.get('cont') not in ['yes', 'no']:
            return make_response('Argument "cont" incorrect', 400)
        continuous = request.args.get('cont')

    if 'text' not in request.args:
         return make_response('No text argument', 400)

    return make_response(jsonify({'aggressiveness': aggressiveness_analyzer(request.args.get('text'), continuous)}), 200)