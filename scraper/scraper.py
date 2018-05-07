__author__ = 'tv'

from libs.article import Article
from libs.multi_thread import multi_thread
from libs.nprscraper import NPRScraperFunctions
from libs.sqlcreator import create_alchemy_engine

import sys
import json
import pickle
import os.path
import argparse


from sqlalchemy.orm import sessionmaker


def is_url_in_db(session, url):
    return session.query(Article).filter(Article.url == url).count() > 0


def run_scraper(config, session, url_queue, urls_traversed):

    count = session.query(Article).count()

    while len(url_queue) > 0:

        print("DB count:", count, "Traversed:", len(urls_traversed), "Queue:", len(url_queue))

        if "max_count" in config:
            if count > config["max_count"]:
                break

        curr_traverse = []
        while len(curr_traverse) < 100 and len(url_queue) > 0:
            url = url_queue.pop()
            if is_url_in_db(session, url):
                continue
            curr_traverse.append(url)

        # Pass that list to multi-threading
        results = multi_thread(NPRScraperFunctions.scrape_url, curr_traverse, 10)

        # Multi-threading should return dictionaries mapping to results and to discovered URLs
        urls_traversed.update(curr_traverse)

        # Create class for DB that maintains unique set of to_traverse and traverse
        for result in results:
            result_dict = result[1]
            if "article" in result_dict:
                session.add(result_dict["article"])

            url_queue = url_queue.union(set(result_dict["urls"]) - urls_traversed)

        # Commit changes, get current database count
        session.commit()
        count = session.query(Article).count()

    return url_queue, urls_traversed

def read_pickle(filename):
    with open(filename, 'rb') as file_hdl:
        return pickle.load(file_hdl)

def write_pickle(filename, object):
    with open(filename, 'wb') as file_hdl:
        pickle.dump(object, file_hdl)

def main(argv):
    parser = argparse.ArgumentParser(description='Scrape NPR website for news')
    parser.add_argument("-c", "--config", help="Configuration JSON", default=None)

    args = parser.parse_args()

    config_file = args.config

    if config_file is None:
        parser.print_help()
        return

    if not os.path.isfile(config_file):
        print("File", config_file, "not found")
        parser.print_help()
        return

    # Create session
    engine = create_alchemy_engine()
    session = sessionmaker(bind=engine)()

    # Read config file
    with open(config_file) as file_hdl:
        config = json.load(file_hdl)

    # Initialize traversed and to traverse sets based on input
    start_url = "https://www.npr.org/"

    if "urls_traversed" in config and os.path.isfile(config["urls_traversed"]):
        urls_traversed = read_pickle(config["urls_traversed"])
    else:
        urls_traversed = set()
    urls_traversed.update([r.url for r in session.query(Article.url).distinct()])

    if "url_queue" in config and os.path.isfile(config["url_queue"]):
        url_queue = read_pickle(config["url_queue"])
        print("URL queue:", len(url_queue))
    else:
        url_queue = set()
    url_queue.add(start_url)

    if start_url in urls_traversed:
        urls_traversed.remove(start_url)

    # ensure any urls we may have traversed are not in there
    url_queue = url_queue - urls_traversed

    print("Starting run with a queue of", len(url_queue))
    # Perform the run
    url_queue, urls_traversed = run_scraper(config, session, url_queue, urls_traversed)

    # Depending on configs, save the remaining list
    if "save_status" in config and config["save_status"]:
        print("Writing url queue with length", len(url_queue))
        write_pickle("url_queue.pkl", url_queue)
        write_pickle("urls_traversed.pkl", urls_traversed)


if __name__ == '__main__':
    main(sys.argv[1:])
