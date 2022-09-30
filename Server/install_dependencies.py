import os
os.system('pip install -r requirements.txt')
from nltk import download
download('vader_lexicon')
download('punkt')
download('wordnet')
download('omw-1.4')
download('averaged_perceptron_tagger')