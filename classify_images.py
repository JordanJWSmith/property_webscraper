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

def generate_location_df(cursor, location, save_path):
    # ITEMS = []
    i = 0

    for listing in cursor:
        
        # load the existing location csv
        save_df = pd.read_csv(save_path)

        ITEMS = []

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

        # skip if image request unsuccessful
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

        # one df per property
        location_df = pd.DataFrame(ITEMS)
        location_df.columns = ['_id', 'property_url', 'display_address', 'bedrooms', 'bathrooms', 'price', 'image_url', 'top_label_score', 'top_label']

        # append the property to the existing csv and save
        concat_df = pd.concat([save_df, location_df], ignore_index=True)
        concat_df.to_csv(save_path, index=False)

    return i


# find a list of the available location codes
location_areas = collection.distinct('location_area')  
done = ['camden', 'city_of_london', 'wandsworth', 'greenwich', 'hackney', 'hammersmith', 'islington', 'kennington', 'kensington_and_chelsea', 'kingston', 'lambeth']
location_areas = [location for location in location_areas if location not in done]

# iterate through each location
for location in location_areas:

    save_path = f'image_classification/{location}_image_classification.csv'

    if not os.path.isfile(save_path):
        init_df = pd.DataFrame(columns=['_id', 'property_url', 'display_address', 'bedrooms', 'bathrooms', 'price', 'image_url', 'top_label_score', 'top_label'])
        init_df.to_csv(save_path, index=False)

    save_df = pd.read_csv(save_path)
    existing_ids = list(set(save_df['_id'].tolist()))

    # ids from df are <int>, ids from mongo are <str>
    existing_ids = [str(i) for i in existing_ids]

    # load listings from given location that haven't been processed yet
    mongo_query = {'location_area': location, 'id': { '$nin': existing_ids }}

    count_docs = collection.count_documents(mongo_query)

    # smaller batch size stops it crashing at ~100 properties
    cursor = collection.find(mongo_query, batch_size=25)

    logging.info(f"Classifying {count_docs} listings from {location}")

    # run all properties for that location through the model
    num_processed = generate_location_df(cursor, location, save_path)

    logging.info(f"Processed {num_processed} listings from {location}")

    # location_df.to_csv(f'image_classification/{location}_image_classification.csv')

            