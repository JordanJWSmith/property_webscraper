import os
import json
import logging
from dotenv import load_dotenv
from pymongo import MongoClient, errors

# from insert_to_mongo import insert_many_to_mongo
from scrape_utils import save_json, scrape_location, process_search_page, insert_many_to_mongo


load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
MONGO_COLLECTION = os.getenv('MONGO_CLUSTER')

db_name = 'property_data'
collection_name = 'properties'


user_agent = 'Mozilla/5.0 (Linux; Android 10; SM-A205U) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/106.0.5249.126 Mobile Safari/537.36'

location_codes = {'kennington': '5E93977', 'lambeth': '5E93971', 'hammersmith': '5E61407', 'southwark': '5E61518', 'richmond': '5E1127', 'wandsworth': '5E93977'}

num_pages = 999 // 24
line_break = '*'*20
prop_count = 0

for location, code in location_codes.items():
    logging.info(f'{line_break} Beginning scraping from {location} {line_break}')

    location_properties = scrape_location(location, code, num_pages, user_agent)

    inserted_property_count = insert_many_to_mongo(db_name, collection_name, location_properties)
    save_json(f'json_data/{location}', location_properties)

    prop_count += inserted_property_count

logging.info(f'{prop_count} properties written to MongoDB in total')







