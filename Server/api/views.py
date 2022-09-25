from flask import Blueprint, request, jsonify, make_response
from api.python_utils import sentiment_analyzer, tokenizeSentence, tokenizeWords, wordFreq, remStopwords, stemmer, lemmatizer, pos_tagger, analysis_sentiment_analyzer, aggressiveness_analyzer, getPunctuationCount, posWordsAnalysis, wordFreqAnalysis, analysis_aggressiveness_analyzer, checkAuthToken, produceHashFromText, sendValidationEmail, getLastHistoryTexts;
from urllib.parse import unquote
import json
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Text_Log
from . import db

def log_text(auth_key, parameters, text, rest):
    new_text = Text_Log(auth_key = auth_key, parameters = parameters, text = text, rest = rest)
    db.session.add(new_text)
    db.session.commit()

views = Blueprint('views', __name__)

@views.route('/login_user', methods=['GET'])
def login_user():
    res = json.loads(request.json)
    user = User.query.filter_by(email=res.get('email')).first()
    if user:
        if check_password_hash(user.password, res.get('password')):
            return make_response(jsonify({'id':user.id,'email':user.email,'password':user.password,'is_authed':user.is_authed, 'auth_key':user.auth_key, 'mail_auth_key': user.mail_auth_key}),200)
        else:
            return make_response('Incorrect Login', 400)
    else:
        return make_response('Incorrect Login', 400)

@views.route('/load_user', methods=['GET'])
def load_user():
    res = json.loads(request.json)
    user = User.query.filter_by(id=res.get('id')).first()
    if user:
        return make_response(jsonify({'id':user.id,'email':user.email,'password':user.password,'is_authed':user.is_authed, 'auth_key':user.auth_key, 'mail_auth_key': user.mail_auth_key}),200)
    else:
        return make_response('User not found', 400)

@views.route('/register_user', methods=['POST'])
def register_user():
    res = json.loads(request.json)
    user = User.query.filter_by(email=res.get('email')).first()
    if user:
        return make_response(jsonify({'reason': 'E-mail is already used.'}), 400)
    else:
        if (res.get('p1') != res.get('p2')):
            return make_response(jsonify({'reason': 'Passwords don\'t match.'}), 400)
        elif (len(res.get('p1'))<6):
            return make_response(jsonify({'reason': 'Password must be at least 6 characters.'}),400)
        else:
            new_user = User(email=res.get('email'), password=generate_password_hash(res.get('p1'), method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            user = User.query.filter_by(email=res.get('email')).first()
            user.mail_auth_key = produceHashFromText(str(user.id))
            db.session.commit()

            sendValidationEmail(res.get('email'), produceHashFromText(str(user.id)), res.get('front_url'))

            return make_response(jsonify({'id':user.id,'email':user.email,'password':user.password,'is_authed':user.is_authed, 'auth_key':user.auth_key, 'mail_auth_key': user.mail_auth_key}),200)

@views.route('/delete_user', methods=['POST'])
def delete_user():
    res = json.loads(request.json)
    user = User.query.filter_by(id=res.get('user_id')).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return make_response("User deleted",200)
    else:
        return make_response('User not found', 400)

@views.route('/resend_verification', methods=['POST'])
def resend_verification():
    res = json.loads(request.json)
    user = User.query.filter_by(id=res.get('user_id')).first()
    if user:
        sendValidationEmail(user.email, produceHashFromText(str(user.id)), res.get('front_url'))
        return make_response("User deleted",200)
    else:
        return make_response('User not found', 400)

@views.route('/verify_user', methods=['POST'])
def verify_user():
    res = json.loads(request.json)
    user = User.query.filter_by(mail_auth_key=res.get('auth_key')).first()
    if user:
        user.is_authed = True
        user.auth_key = produceHashFromText(str(user.email) + str(user.password))
        db.session.commit()
        return make_response("User verified",200)
    else:
        return make_response('User not found', 400)

@views.route('/get_user_history', methods=['GET'])
def get_user_history():
    res = json.loads(request.json)
    if ('auth_key' in res):
        user = User.query.filter_by(auth_key=res.get('auth_key')).first()
        if user:
            last_records = getLastHistoryTexts(res.get('auth_key'))
            return make_response(jsonify({'last_records': last_records}), 200)
    else:
        return make_response('Auth not found', 400)

@views.route('/analyze_front', methods=['GET'])
def analyze_front():
    res = json.loads(request.json)
    inserted_text = res.get('inserted_text')
    is_authed = res.get('is_authed')

    if (is_authed):
        sentiment_score = analysis_sentiment_analyzer(inserted_text)
        aggressiveness_score = analysis_aggressiveness_analyzer(inserted_text)
    else:
        sentiment_score = 0
        aggressiveness_score = 0

    if (is_authed):
        user = User.query.filter_by(auth_key=res.get('auth')).first()
        if user:
            log_text(res.get('auth'),'',unquote(inserted_text), False)

    return make_response(jsonify({'pos': posWordsAnalysis(inserted_text), 
                                'len': len(inserted_text),
                                'tokens_word': len(tokenizeWords(inserted_text)),
                                'tokens_sent': len(tokenizeSentence(inserted_text)),
                                'punkt': getPunctuationCount(inserted_text),
                                'freq_anal': wordFreqAnalysis(inserted_text),
                                'sentiment_anal': sentiment_score,
                                'sentiment_aggr': aggressiveness_score}), 200)

@views.route('/api/tokenize', methods=['GET'])
def tokenize():
    authed = False
    if 'auth' in request.args:
        authed = True

    if 'text' in request.args:
        if (authed):
            log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

        return make_response(jsonify({'sentence_tokens': tokenizeSentence(request.args.get('text')), 'word_tokens': tokenizeWords(request.args.get('text'))}), 200)
    else:
        return make_response("No text argument", 400)

@views.route('/api/frequency', methods=['GET'])
def frequency():
    authed = False
    if 'auth' in request.args:
        authed = True

    if 'text' in request.args:
        if 'level' in request.args:
            if request.args.get('level') in ['char','word']:
                if (authed):
                    log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

                return make_response(jsonify({'word_frequency': wordFreq(request.args.get('text'), request.args.get('level'))}), 200)
            else:
                return make_response('Argument "level incorrect', 400)
        else:
            if (authed):
                log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

            return make_response(jsonify({'word_frequency': wordFreq(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/stopwords', methods=['GET'])
def stopwrds():
    if 'text' in request.args:
        authed = False
        if 'auth' in request.args:
            authed = True

        tokens = False
        sw = []
        if 'tokens' in request.args:
            if unquote(request.args.get('tokens')) in ['yes','no']:
                tokens = True if request.args.get('tokens')=='yes' else False
            else:
                return make_response('Argument "tokens" incorrect', 400)

        if 'sw_list' in request.args:
            sw = request.args.get('sw_list')

        if (authed):
            log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)
        
        return make_response(jsonify({'text': remStopwords(request.args.get('text'), sw = sw, tokens=tokens)}), 200)

    else:
        return make_response('No text argument', 400)

@views.route('/api/stemming', methods=['GET'])
def stem():
    authed = False
    if 'auth' in request.args:
        authed = True

    if 'text' in request.args:
        if 'stemmer' in request.args:
            if request.args.get('stemmer') in ['porter','snowball']:
                if (authed):
                    log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

                return make_response(jsonify({'stemmed_string': stemmer(request.args.get('text'), request.args.get('stemmer'))}), 200)
            else:
                return make_response('Argument "stemmer" incorrect', 400)
        else:
            if (authed):
                log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

            return make_response(jsonify({'stemmed_string': stemmer(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/lemmatization', methods=['GET'])
def lemmatize():
    authed = False
    if 'auth' in request.args:
        authed = True

    if 'text' in request.args:
        if (authed):
            log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

        return make_response(jsonify({'lemmatized_string': lemmatizer(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/pos', methods=['GET'])
def pos_tagging():
    authed = False
    if 'auth' in request.args:
        authed = True

    if 'text' in request.args:
        if (authed):
            log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

        return make_response(jsonify({'tokens': tokenizeWords(request.args.get('text')),'pos_tags': pos_tagger(request.args.get('text'))}), 200)
    else:
        return make_response('No text argument', 400)

@views.route('/api/sentiment', methods=['GET'])
def sentimentize():
    authed = False
    if 'auth' in request.args:
        authed = True

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

    if (authed):
        log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

    return make_response(jsonify({'sentiment': sentiment_analyzer(text = request.args.get('text'), method = method, continuous=continuous)}), 200)

@views.route('/api/aggressiveness', methods=['GET'])
def aggressiveness():
    authed = False
    if 'auth' in request.args:
        authed = True

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

    if (authed):
        log_text(request.args.get('auth'), request.json, unquote(request.args.get('text')),True)

    return make_response(jsonify({'aggressiveness': aggressiveness_analyzer(request.args.get('text'), continuous)}), 200)