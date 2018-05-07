# Scalar-Project
Web scraper for NPR's website that scrapes news articles, and adds them to a database.  A Flask application displays and allows searching of the articles. 

*** 

## /scraper

The entirety of the web scraper resides in this folder. 

* scraper.py - the entry point for running the scraper.  Instructions for running are below. 
* config.json - config file for running the scraper.  Additional options need to be added, still in progress.
* Scalar Scraper.ipynb - Jupter notebook used to develop the functions used here.  Not relevant to running the scraper. 
* libs - library folder for locally written libraries. 
  * article.py - defines the article class that gets written to the database
  * multi_thread.py - adds multi-threading functionality
  * nprscraper.py - defines the functionality for actually scraping the website
  * sqlcreator.py - defines the database that we connect to.  currently this is set to a sqlite database, but to connect to any other database type, this is the file to modify. 

To run the web scraper

'''
python scraper.py
'''

Without arguments, the output will look like:

'''
usage: scraper.py [-h] [-c CONFIG]

Scrape NPR website for news

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration JSON
'''

To run the scraper with a config file

'''
python scraper.py -c config.json
'''

As it's currently set up, a sqlite database will be created one level up, in the main folder.  This way, both the scraper and the web server will have access to it. 

*** 
## /web

The database created by the scraper is used in the web server. 

To start the web server, run 

'''
python flaskNews.py
'''

To modify what database the web server uses, modify the libs/sqlcreator.py file to match the one in the scraper. 
