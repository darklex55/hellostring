from .models import User

from hashlib import sha256
from urllib.parse import unquote
from json import dumps

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk import pos_tag
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from textblob import TextBlob

import pickle
import lightgbm
import string
from collections import Counter

def produceHashFromText(text):
    text = text.encode('UTF-8')
    return sha256(text).hexdigest()

def sendValidationEmail(email, auth_key, url_root):
    url_root_c = url_root
    if (url_root_c[-1]=='/'):
        url_root_c = url_root_c[:-1]
    msg = MIMEMultipart()
    msg['Subject'] = 'HelloString Account Verification'
    msg['From'] = 'darklex55server@gmail.com'
    text = 'Please validate your account by clicking the following link: '+ url_root_c +'/verification?auth_key='+ auth_key
    msg.attach(MIMEText(text,'plain'))
    smtp = smtplib.SMTP('smtp.gmail.com:587')
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login('darklex55server@gmail.com','qpvfntgdvddadhqo')
    smtp.sendmail('darklex55server@gmail.com',email,msg.as_string())
    smtp.quit()

def checkAuthToken(auth_token):
    stored_user = User.query.filter_by(auth_key=auth_token).first()
    if stored_user:
        return True
    return False

def tokenizeSentence(text):
    return sent_tokenize(unquote(text))

def tokenizeWords(text):
    return word_tokenize(unquote(text))

def getPunctuationCount(text):
    return sum([1 for char in unquote(text) if char in string.punctuation])

def wordFreq(text, level='word'):
    if level=='word':
        return dumps(dict(FreqDist(tokenizeWords(unquote(text).lower()))))
    else:
        return dumps(dict(FreqDist(unquote(text).lower())))

def wordFreqAnalysis(text):
    data = dict(FreqDist(tokenizeWords(unquote(text).lower())))
    data_sorted = sorted(data, key=data.get, reverse=True)
    return [data_sorted, [data.get(val) for val in data_sorted]]

def remStopwords(text, sw=[], tokens=True):
    filtered_sent=[]
    if len(sw)>0:
        sw = unquote(sw).replace(' ','').split(',')
        for w in word_tokenize(unquote(text)):
            if w not in sw:
                filtered_sent.append(w)
        if tokens:
            return filtered_sent
        else:
            detok = TreebankWordDetokenizer()
            return detok.detokenize(filtered_sent)
            
    else:
        stop_words=set(stopwords.words("english"))
        for w in word_tokenize(unquote(text)):
            if w not in stop_words:
                filtered_sent.append(w)
        if tokens:
            return filtered_sent
        else:
            detok = TreebankWordDetokenizer()
            return detok.detokenize(filtered_sent)

def stemmer(text, stemmer='porter'):
    detok = TreebankWordDetokenizer()
    if stemmer=='porter':
        ps = PorterStemmer()
        return detok.detokenize([ps.stem(w) for w in tokenizeWords(text)])
    if stemmer=='snowball':
        ps = SnowballStemmer("english")
        return detok.detokenize([ps.stem(w) for w in tokenizeWords(text)])

def lemmatizer(text):
    detok = TreebankWordDetokenizer()
    ps = WordNetLemmatizer()
    return detok([ps.lemmatize(w) for w in tokenizeWords(text)])

def pos_tagger(text):
    return [i[1] for i in pos_tag(tokenizeWords(text))]

def posWordsAnalysis(text):
    tokens = tokenizeWords(text)
    pos_tags = pos_tagger(text)
    pos_dict = {'CC': 'cc', 'CD': 'cd', 'DT': 'dt', 'EX': 'ex', 'FW': 'fw',  'IN': 'in',  'JJ': 'jj', 'JJR': 'jj', 'JJS': 'jj', 'LS': 'ls', 'MD': 'md', 'NN': 'nn',
    'NNS': 'nn', 'NNP': 'nn', 'NNPS': 'nn', 'PDT': 'pdt', 'POS': 'pos', 'PRP': 'pr', 'PRP$': 'pr', 'RB': 'rb', 'RBR': 'rb', 'RBS': 'rb', 'RP': 'rp', 'TO': 'to', 
    'UH': 'uh', 'VB': 'vb', 'VBG': 'vb', 'VBD': 'vb', 'VBN': 'vb', 'VBP': 'vb', 'VBZ': 'vb', 'WDT': 'wh', 'WP': 'wh', 'WRB': 'wh', '.': 'punc'}
    pos_dict_real = {'CC': 'Conjuction', 'CD': 'Cardinal', 'DT': 'Determiner', 'EX': 'Existential', 'FW': 'Foreign Word',  'IN': 'Preposition',  'JJ': 'Adjective', 'JJR': 'Adjective', 'JJS': 'Adjective', 'LS': 'List Market', 'MD': 'Modal', 'NN': 'Noun',
    'NNS': 'Noun', 'NNP': 'Noun', 'NNPS': 'Noun', 'PDT': 'Predeterminer', 'POS': 'Possessive', 'PRP': 'Pronoun', 'PRP$': 'Pronoun', 'RB': 'Adverb', 'RBR': 'Adverb', 'RBS': 'Adverb', 'RP': 'Adverb', 'TO': 'Marker', 
    'UH': 'Interjection', 'VB': 'Verb', 'VBG': 'Verb', 'VBD': 'Verb', 'VBN': 'Verb', 'VBP': 'Verb', 'VBZ': 'Verb', 'WDT': 'Determiner', 'WP': 'Determiner', 'WRB': 'Determiner', '.': 'Punctuation', 'other': 'Other'}
    html_string = ''
    for i in range(len(tokens)):
        html_string+='<span onclick="location.href="#";" style="cursor: pointer;" class="' + pos_dict.get(pos_tags[i], 'other') + '"><span class="hovertext" data-hover="' + pos_dict_real.get(pos_tags[i],'other') + '">' + tokens[i] +' </span></span>'
        #html_string+='<span class="hovertext" data-hover="' + pos_dict_real.get(pos_tags[i],'other') + '">' + tokens[i] +' </span>'
    return html_string

def sentiment_analyzer(text, method, continuous):
    continuous = True if continuous == 'yes' else False
    text = unquote(text)

    if method == 'vader':
        sid = SentimentIntensityAnalyzer()
        score = sid.polarity_scores(text).get('compound')

        if continuous:
            return score
        else:
            if score>0.25:
                return 1
            elif score<-0.25:
                return -1
            else:
                return 0

    if method =='textblob':
        score = TextBlob(text).sentiment.polarity

        if continuous:
            return score
        else:
            if score>0.25:
                return 1
            elif score<-0.25:
                return -1
            else:
                return 0

def aggressiveness_analyzer(text, continuous):
    lematizer = WordNetLemmatizer()
    vectorizer = pickle.load(open('models/tfidf_vectorizer.pickle','rb'))
    continuous = True if continuous == 'yes' else False

    slangs = {}
    with open("models/slangs.txt") as f:
        for line in f:
            (key, val) = (line.split()[0], line.split()[1].split(','))
            slangs[key] = val
    contraction_patterns = [ (r'won\'t', 'will not'), (r'can\'t', 'cannot'), (r'i\'m', 'i am'), (r'ain\'t', 'is not'), (r'(\w+)\'ll', '\g<1> will'), (r'(\w+)n\'t', '\g<1> not'),
                            (r'(\w+)\'ve', '\g<1> have'), (r'(\w+)\'s', '\g<1> is'), (r'(\w+)\'re', '\g<1> are'), (r'(\w+)\'d', '\g<1> would'), (r'&', 'and'), (r'dammit', 'damn it'), (r'dont', 'do not'), (r'wont', 'will not') ]

    def lemmatization(tokens_obj):
        return ([lematizer.lemmatize(token) for token in tokens_obj[0]] , tokens_obj[1], tokens_obj[2])

    def tokenizer(txt, capital_tag=False):
        if (capital_tag):
            tokens = word_tokenize(txt)
            if len(tokens)>0:
                tokens[0] = tokens[0].lower()
                for i in range(len(tokens)-1):
                    if (tokens[i+1][0].isupper() and tokens[i] not in ['.','!','?']):
                        tokens[i+1] = 'cptl' + tokens[i+1].lower()
                    else:
                        tokens[i+1] = tokens[i+1].lower()
            return tokens
        else:
            return word_tokenize(txt.lower())

    def count_slangs(txt):
        cnt = 0
        for tok in txt.split():
            if slangs.get(tok):
                cnt+=1
        return cnt

    def sentence_pnkt(sentence):
        return '{Q}' if sentence[-1]=='?' else ('{E}' if sentence[-1]=='!' else '{P}')

    def sentences(txt):
        return [(sen.translate(str.maketrans('', '', string.punctuation)), sentence_pnkt(sen)) for sen in sent_tokenize(txt)]

    def sentences_tokenizer(txt, capital_tag=False):
        return [(tokenizer(sen[0], capital_tag),sen[1]) for sen in sentences(txt)]

    def tokens_all(txt, capital_tag=False):
        S_obj = sentences_tokenizer(txt,capital_tag)
        important_features = [txt.count(punk) for punk in ['[',']','*','"']]
        important_features.append(sum([1 if s.isdigit() else 0 for s in txt.split()]))
        important_features.append(count_slangs(txt))
        cntr = Counter([S[1] for S in S_obj])
        return [token for sentence in [S[0] for S in S_obj] for token in sentence], [cntr['{P}'],cntr['{Q}'],cntr['{E}']], important_features

    tokens = ' '.join(lemmatization(tokens_all(text,False))[0])

    vector = vectorizer.transform([tokens]).toarray()

    model = lightgbm.Booster(model_file='models/hellostring_aggressiveness.model')
   
    score = model.predict(vector)[0]

    if score>1:
        score = 1

    if continuous:
        return score
    else:
        if score>0.3:
            return 1
        else:
            return 0

def analysis_sentiment_analyzer(text):
    return round(1000*sentiment_analyzer(text,'vader','yes'))/1000

def analysis_aggressiveness_analyzer(text):
    return round(1000*aggressiveness_analyzer(unquote(text),'yes'))/1000