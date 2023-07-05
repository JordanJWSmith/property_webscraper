import os
import json
import logging
import requests
from tqdm import tqdm
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient, errors
from collections import Counter

load_dotenv()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

user_agent = 'Mozilla/5.0 (Linux; Android 10; SM-A205U) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/106.0.5249.126 Mobile Safari/537.36'

location_codes = {'kennington': '5E93977', 'lambeth': '5E93971', 'hammersmith': '5E61407', 'southwark': '5E61518'}

# num_pages = 999 // 24
# num_pages = 4

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
MONGO_COLLECTION = os.getenv('MONGO_CLUSTER')

db_name = 'property_data'
collection_name = 'properties'


def save_json(location, properties):
    timestring = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
    with open(f'{location}_properties_{timestring}.json', 'w', encoding='utf-8') as f:
        json.dump(properties, f, ensure_ascii=False, indent=4)


def insert_many_to_mongo(db_name, collection_name, properties):
    cluster = MongoClient(f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_COLLECTION}")
    db = cluster[db_name]
    collection = db[collection_name]

    existing_property_ids = [str(i) for i in collection.distinct('_id')]
    properties_to_insert = [prop for prop in properties if prop['_id'] not in existing_property_ids]
    collection.insert_many(properties_to_insert)

    logging.info(f'{len(properties_to_insert)} properties written to MongoDB')

    return len(properties_to_insert)

    # print(properties_to_insert)

    # print(property_ids[:10])

    # try:
    #     collection.insert_many(properties)
    # except errors.BulkWriteError as e:
    #     pass


def scrape_location(location, location_code, num_pages, user_agent):
    location_properties = []
    for i in range(num_pages):
        logging.info(f"SCRAPING PAGE {i+1} OF {num_pages} in {location.upper()}")

        index = i*24
        search_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{location_code}&index={index}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='
        html_page = requests.get(search_url, headers={'User-Agent': user_agent})
        soup = BeautifulSoup(html_page.content, 'html.parser')
        page_properties = process_search_page(soup, location)
        location_properties += (page_properties)
    
    # save_json(location, location_properties)
    return location_properties


def process_search_page(soup, location):
    page_properties = []
    for s in soup.find_all('script'):
        if 'window.jsonModel = ' in s.text:
            str_dict = s.text.strip()[19:]
            properties_dict = json.loads(str_dict)['properties']

            for prop in tqdm(properties_dict):
                property_url = prop['propertyUrl']
                property_page = requests.get(f'https://www.rightmove.co.uk{property_url}', headers={'User-Agent': user_agent})
                property_soup = BeautifulSoup(property_page.content, 'html.parser')

                for t in property_soup.find_all('script'):
                    if 'window.PAGE_MODEL =' in t.text:
                        property_str_dict = t.text.strip()[20:]
                        property_page_dict = json.loads(property_str_dict)
                        property_page_data = property_page_dict['propertyData']
                        for key in property_page_data:
                            prop[key] = property_page_data[key]

                prop['_id'] = prop['id']
                prop['location_area'] = location
                page_properties.append(prop)
                
    return page_properties


# def scrape_all_locations(location_codes, num_pages, user_agent, write_to_mongo):
#     all_location_properties = []
#     line_break = '*'*20
#     for location, code in location_codes.items():
#         logging.info(f'{line_break} Beginning scraping from {location} {line_break}')
#         location_properties = scrape_location(location, code, num_pages, user_agent)
#         all_location_properties.append(location_properties)
    
#     save_json('all_locations', all_location_properties)
#     return all_location_properties


# test_ids = ['106242428', '106913681', '108500255', '110218751', '111137990', '111896183', '114052802', '114306314', '114542921', '116069828', 'This should remain']
# test_properties = [{'_id': test_id, 'title': 'etc'} for test_id in test_ids]
# # print(test_properties)
# insert_many_to_mongo(db_name, collection_name, test_properties)