__author__ = 'tv'

import re
import string
import requests

from bs4 import BeautifulSoup
from collections import Counter

from libs.article import Article

STOPWORDS = {'fire', 'who', 'seem', 'hereupon', 'seemed', 'twenty', 'dont', 'ten', 'beside', 'meanwhile', 'back', 'we', 'give', 'thru', 'became', 'i', 'upon', 'since', 'themselves', 'un', 'your', 'whole', 'throughout', 'without', 'its', 'besides', 'three', 'front', 'interest', 'between', 'hers', 'than', 'noone', 'everyone', 'six', 'keep', 'why', 'perhaps', 'mill', 'of', 'a', 'anyhow', 'other', 'latter', 'has', 'made', 'couldnt', 'up', 'describe', 'even', 'nine', 'again', 'said', 'toward', 'was', 'anyone', 'find', 'must', 'beyond', 'too', 'whence', 'anything', 'two', 'around', 'yourself', 'these', 'inc', 'it', 'been', 'in', 'well', 'can', 'were', 'me', 'move', 'most', 'amongst', 'few', 'about', 'nevertheless', 'else', 'first', 'sometime', 'among', 'what', 'top', 'become', 'hundred', 'whereupon', 'after', 'side', 'except', 'seems', 'then', 'along', 'same', 'bill', 'onto', 'thereby', 'hereafter', 'during', 'thick', 'towards', 'is', 'behind', 'out', 'still', 'hes', 'where', 'name', 'whether', 'my', 'yourselves', 'might', 'elsewhere', 'fifty', 'found', 'empty', 'now', 'ie', 'amount', 'are', 'mostly', 'very', 'via', 'wherein', 'hereby', 'within', 'whoever', 'should', 'itself', 'something', 'last', 'full', 'wherever', 'thereupon', 'against', 'no', 'one', 'below', 'done', 'never', 'please', 'here', 'someone', 'nor', 'whatever', 'thence', 'con', 'therefore', 'show', 'each', 'becoming', 'way', 'the', 'from', 'own', 'former', 'they', 'least', 'thus', 'because', 'etc', 'herself', 'ever', 'would', 'she', 'nowhere', 'almost', 'her', 'once', 'due', 'eight', 'others', 'any', 'next', 'had', 'not', 'co', 'down', 'our', 'myself', 'get', 'often', 'says', 'five', 'though', 'every', 'latterly', 'im', 'when', 'hence', 'everything', 'off', 'anyway', 'more', 'enough', 'everywhere', 'ours', 'thin', 'less', 'by', 'system', 'could', 'neither', 'none', 'them', 'whereby', 'ltd', 'either', 'on', 'cry', 'or', 'thereafter', 'such', 'may', 'yet', 'moreover', 'becomes', 'over', 'you', 'cannot', 'him', 'all', 'amoungst', 'otherwise', 'herein', 'that', 'therein', 'whereas', 'which', 'while', 'have', 'if', 'beforehand', 'however', 'to', 'under', 'further', 'do', 'somehow', 'so', 'himself', 'there', 'through', 'yours', 'will', 'nothing', 'above', 'call', 'together', 'this', 'and', 'as', 'fill', 'eleven', 'ourselves', 'at', 'hasnt', 'already', 'another', 'some', 'see', 'anywhere', 'an', 're', 'whose', 'forty', 'part', 'rather', 'nobody', 'alone', 'bottom', 'he', 'cant', 'both', 'several', 'many', 'twelve', 'go', 'also', 'indeed', 'eg', 'namely', 'afterwards', 'for', 'per', 'sometimes', 'always', 'be', 'much', 'four', 'de', 'third', 'mine', 'detail', 'those', 'serious', 'how', 'although', 'put', 'sixty', 'whither', 'their', 'take', 'whom', 'being', 'fifteen', 'until', 'across', 'formerly', 'but', 'am', 'his', 'somewhere', 'thats', 'with', 'before', 'say', 'sincere', 'whereafter', 'into', 'whenever', 'seeming', 'only', 'us'}


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

