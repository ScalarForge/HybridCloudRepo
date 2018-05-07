__author__ = 'tv'

from libs.article import Article
from libs.multi_thread import multi_thread
from libs.nprscraper import NPRScraperFunctions
from libs.sqlcreator import create_alchemy_engine

import sys
import os.path
import argparse

from sqlalchemy.orm import sessionmaker


def is_url_in_db(session, url):
    return session.query(Article).filter(Article.url == url).count() > 0


def run_scraper(config, session, url_queue, urls_traversed):

    count = session.query(Article).count()

    while len(url_queue):

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


def main(argv):
    parser = argparse.ArgumentParser(description='Scrape NPR website for news')
    parser.add_argument("-c", "--config", help="Configuration JSON", default=None)

    args = parser.parse_args()

    config = args.config

    if config is None:
        parser.print_help()
        return

    if not os.path.isfile(config):
        print("File", config, "not found")
        parser.print_help()
        return

    # Create session
    engine = create_alchemy_engine()
    session = sessionmaker(bind=engine)()

    # Read config file
    # Initialize traversed and to traverse sets based on input

    start_url = "https://www.npr.org/"

    urls_traversed = set()
    urls_traversed.update([r.url for r in session.query(Article.url).distinct()])

    url_queue = set()
    url_queue.add(start_url)
    if start_url in urls_traversed:
        urls_traversed.remove(start_url)

    # Perform the run
    run_scraper(config, session, url_queue, urls_traversed)

    # Depending on configs, save the remaining list

if __name__ == '__main__':
    main(sys.argv[1:])
