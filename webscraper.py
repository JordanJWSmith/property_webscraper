import os
import json
import logging
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

load_dotenv()

class Webscraper:
    def __init__(self, db_name, collection_name, user_agent, location_codes, num_pages):
        self.db_name = db_name
        self.collection_name = collection_name
        self.user_agent = user_agent
        self.location_codes = location_codes
        self.num_pages = num_pages
        self.MONGO_USER = os.getenv('MONGO_USER')
        self.MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
        self.MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
        self.MONGO_COLLECTION = os.getenv('MONGO_CLUSTER')


    def insert_many_to_mongo(self, properties):
        cluster = MongoClient(f"mongodb+srv://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_CLUSTER}/{self.MONGO_COLLECTION}")
        db = cluster[self.db_name]
        collection = db[self.collection_name]

        existing_property_ids = [str(i) for i in collection.distinct('_id')]
        properties_to_insert = [prop for prop in properties if prop['_id'] not in existing_property_ids]
        collection.insert_many(properties_to_insert)

        logging.info(f'{len(properties_to_insert)} new properties written to MongoDB')

        return len(properties_to_insert)


    def save_json(self, location, properties):
        timestring = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
        with open(f'{location}_properties_{timestring}.json', 'w', encoding='utf-8') as f:
            json.dump(properties, f, ensure_ascii=False, indent=4)


    def scrape_location(self, location, location_code):
        location_properties = []
        for i in range(self.num_pages):
            logging.info(f"SCRAPING PAGE {i+1} OF {self.num_pages} in {location.upper()}")

            index = i*24
            search_url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{location_code}&index={index}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='
            html_page = requests.get(search_url, headers={'User-Agent': self.user_agent})
            soup = BeautifulSoup(html_page.content, 'html.parser')
            page_properties = self.process_search_page(soup, location)
            location_properties += (page_properties)
        
        return location_properties
        

    def process_search_page(self, soup, location):
        page_properties = []
        for s in soup.find_all('script'):
            if 'window.jsonModel = ' in s.text:
                str_dict = s.text.strip()[19:]
                properties_dict = json.loads(str_dict)['properties']

                for prop in tqdm(properties_dict):
                    property_url = prop['propertyUrl']
                    property_page = requests.get(f'https://www.rightmove.co.uk{property_url}', headers={'User-Agent': self.user_agent})
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

    
    def scrape(self):
        line_break = '*'*20
        prop_count = 0
        for location, code in self.location_codes.items():
            logging.info(f'{line_break} Beginning scraping from {location} {line_break}')

            location_properties = self.scrape_location(location, code)

            inserted_property_count = self.insert_many_to_mongo(location_properties)
            self.save_json(f'json_data/{location}', location_properties)

            prop_count += inserted_property_count

        logging.info(f'{prop_count} properties written to MongoDB in total')
