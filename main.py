import json
import logging
from webscraper import Webscraper

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def main():
    db_name = 'property_data'
    collection_name = 'properties'
    
    user_agent = 'Mozilla/5.0 (Linux; Android 10; SM-A205U) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Chrome/106.0.5249.126 Mobile Safari/537.36'

    with open('location_codes.json', 'r') as f:
        location_codes = json.load(f)
    
    num_pages = 999 // 24  # Number of pages to scrape per location (24 properties per page)

    TestClass = Webscraper(db_name, collection_name, user_agent, location_codes, num_pages)
    TestClass.scrape()


if __name__ == "__main__":
    main()
