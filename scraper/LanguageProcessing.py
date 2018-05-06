import nltk
import string

try:
    from geotext import GeoText
except:
    pass

from collections import Counter

from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS

class NLTKProcessing:
    
    stop_words = set(ENGLISH_STOP_WORDS)
    
    def __init__(self, text):
        self._text = text
        self._tagged = nltk.pos_tag(nltk.word_tokenize(text))
        self._nouns = None
        self._prop_nouns = None
        self._verbs = None
        self._most_common = None
        self._geoplaces = None
        
        
    def get_nouns(self):
        if not self._nouns:
            self._nouns = [word for (word, pos) in tagged if pos[:2] == "NN" and len(word) > 1]
        return self._nouns
    
    def get_proper_nouns(self):
        if not self._prop_nouns:
            self._prop_nouns = [word for (word, pos) in tagged if pos == "NNP" and len(word) > 1]
        return self._prop_nouns
    
    def get_verbs(self):
        if not self._verbs:
            self._verbs = [word for (word, pos) in tagged if pos == "VB" and len(word) > 1]
        return self._verbs
    
    def get_most_common(self):
        
        exclude = set(string.punctuation)
        text_nopunct = ''.join(ch for ch in self._text if ch not in exclude)
        
        words = text_nopunct.lower().split(" ")
        words = [word for word in words if word not in NLTKProcessing.stop_words and len(word) > 1]
        
        return Counter(words).most_common(15)
    
    def get_cities(self):
        if not self._geoplaces:
            self._geoplaces = GeoText(self._text)
        return self._geoplaces.cities
    
    def get_country_codes(self):
        if not self._geoplaces:
            self._geoplaces = GeoText(self._text)
        return self._geoplaces.country_mentions