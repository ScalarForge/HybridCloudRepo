# Scalar-Project
Web scraper for NPR's website that scrapes news articles, and adds them to a database.  A Flask application displays and allows searching of the articles. 

## /scraper

The scraper folder contains a number of files. 

* scraper.py - the entry point for running the scraper.  Instructions for running are below. 
* libs - library folder for locally written libraries. 
  * article.py - defines the article class that gets written to the database
  * multi_thread.py - adds multi-threading functionality
  * nprscraper.py - defines the functionality for actually scraping the website
  * sqlcreator.py - defines the database that we connect to.  currently this is set to a sqlite database, but to connect to any other database type, this is the file to modify. 
