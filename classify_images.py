import os
import json
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo import MongoClient
from transformers import pipeline

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

# find a list of the available location codes
location_areas = collection.distinct('location_area')  
location_areas = ['camden']

# iterate through them in batches
for location in location_areas:
    count_docs = collection.count_documents({'location_area': location})
    cursor = collection.find({'location_area': location})

    logging.info(f"Classifying {count_docs} listings from {location}")

    ITEMS = []
    for listing in tqdm(cursor):
        _id = listing['id']
        display_address = listing['displayAddress']
        bedrooms = listing['bedrooms']
        bathrooms = listing['bathrooms']
        price = listing['price']['amount']
        images = listing['propertyImages']['images']

        for image in images:
            image_url = image['srcUrl']
            
            try:
                # find the top scoring class for each image
                result = pipe(image_url, top_k=1)
                score = result[0]['score']
                label = result[0]['label']
            except: 
                logging.info(f"Error with listing {_id}: URL {image_url}")
                score, label = np.nan, np.nan

            # one row per image
            ITEMS.append([_id, display_address, bedrooms, bathrooms, price, image_url, score, label])

    location_df = pd.DataFrame(ITEMS)
    location_df.columns = ['_id', 'display_address', 'bedrooms', 'bathrooms', 'price', 'image_url', 'top_label_score', 'top_label']
    location_df.to_csv(f'image_classification/{location}_image_classification.csv')
            