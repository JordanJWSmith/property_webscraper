import os
import json
import logging
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo import MongoClient
from transformers import pipeline
from PIL import UnidentifiedImageError


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')
HF_TOKEN = os.getenv('HF_TOKEN')

cluster = MongoClient(f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DB_NAME}")
db = cluster[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION]

# hugging face pipeline: https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.ImageClassificationPipeline
pipe = pipeline("image-classification", model="andupets/real-estate-image-classification-30classes")

def generate_location_df(cursor, location):
    ITEMS = []
    i = 0
    for listing in cursor:
        
        _id = listing['id']
        property_url = f'https://www.rightmove.co.uk{listing["propertyUrl"]}'
        display_address = listing['displayAddress']
        bedrooms = listing['bedrooms']
        bathrooms = listing['bathrooms']
        price = listing['price']['amount']
        images = listing['propertyImages']['images']

        if not len(images):
            logging.info(f"{i}) Listing {_id} has no images ({property_url})")
            continue

        i += 1
        logging.info(f"{i}) Processing listing {_id} with {len(images)} images ({property_url})")

        # ping the first image to see if the listing is still live
        if len(images):
            test_image = images[0]['srcUrl']
            test_ping = requests.head(test_image)
        else:
            logging.info(f"{i}) Listing {_id} has no images ({property_url})")
            continue

        if str(test_ping.status_code)[0] == '4':
            logging.info(f"{i}) Listing {_id} appears to no longer be live (status {test_ping.status_code}) ({property_url})")
            continue

        for image in tqdm(images):
            image_url = image['srcUrl']

            try:
                # find the top scoring class for each image
                result = pipe(image_url, top_k=1)
                score = result[0]['score']
                label = result[0]['label']
            except UnidentifiedImageError: 
                ping_image = requests.head(image_url)
                logging.info(f"{i}) UnidentifiedImageError with listing {_id} (status {ping_image.status_code}) ({image_url})")
                score, label = np.nan, np.nan

            # one row per image
            ITEMS.append([_id, property_url, display_address, bedrooms, bathrooms, price, image_url, score, label])

    location_df = pd.DataFrame(ITEMS)
    location_df.columns = ['_id', 'property_url', 'display_address', 'bedrooms', 'bathrooms', 'price', 'image_url', 'top_label_score', 'top_label']

    return location_df


# find a list of the available location codes
location_areas = collection.distinct('location_area')  

# iterate through them in batches
for location in location_areas:
    count_docs = collection.count_documents({'location_area': location})

    # batch size stops it crashing at ~100 properties
    cursor = collection.find({'location_area': location}, batch_size=50)

    logging.info(f"Classifying {count_docs} listings from {location}")

    # run all properties for that location through the model
    location_df = generate_location_df(cursor, location)

    location_df.to_csv(f'image_classification/{location}_image_classification.csv')

            