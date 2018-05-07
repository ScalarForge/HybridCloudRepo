__author__ = 'tv'

import re
import string
import requests

from bs4 import BeautifulSoup
from collections import Counter

from libs.article import Article

from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS

STOPWORDS = set(ENGLISH_STOP_WORDS)
STOPWORDS.update(['said', 'says', 'thats', 'that', 'say', 'dont', 'hes', 'im', 'way'])

class NPRScraperFunctions:
 
    @staticmethod
    def get_most_common(text):
        global STOPWORDS
        
        exclude = set(string.punctuation)
        text_nopunct = ''.join(ch for ch in text if ch not in exclude)

        words = text_nopunct.lower().split(" ")
        words = [word for word in words if word not in STOPWORDS and len(word) > 1]

        return [word for word, count in list(Counter(words).most_common(15))]

    @staticmethod
    def get_text(soup):
        text = ""
        for paragraph in soup.find_all('p'):
            if not paragraph.has_attr('class') and not paragraph.findChildren('b'):
                text += paragraph.get_text() + "\n\n"

        return text

    @staticmethod
    def get_npr_urls(soup):

        pattern = r'20[\d]{2}/[\d]{1,2}/[\d]{1,2}/[\d]+/'

        urls = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            if url.startswith('https://www.npr.org/'):
                if re.search(pattern, url):
                    urls.append(url)

        return urls

    @staticmethod
    def get_title(soup):
        title = ""

        # find href with class == title, then get b
        for link in soup.find_all('a'):
            if link.has_attr('class'):
                if link['class'][0] == "title":
                    title = link.findChildren('b')[0].get_text()

        return title

    @staticmethod
    def get_details(url):
        pattern = r'20[\d]{2}/[\d]{1,2}/[\d]{1,2}/[\d]+/'

        match_object = re.search(pattern, url, flags=0)
        match_split = match_object[0].split("/")

        date = match_split[0] + "-" + match_split[1] + "-" + match_split[2]
        article_id = match_split[3]

        return date, article_id

    @staticmethod
    def scrape_url(url):
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')

        links = NPRScraperFunctions.get_npr_urls(soup)

        text = NPRScraperFunctions.get_text(soup)

        return_dict = {"urls": links}
        if len(text) > 100:
            title = NPRScraperFunctions.get_title(soup)
            date, article_id = NPRScraperFunctions.get_details(url)

            return_dict["article"] = Article(title, text, url, NPRScraperFunctions.get_most_common(text), date)

        return return_dict

