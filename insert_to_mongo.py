import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
MONGO_COLLECTION = os.getenv('MONGO_CLUSTER')

db_name = 'property_data'
collection_name = 'properties'



def insert_many_to_mongo(db_name, collection_name, properties):
    cluster = MongoClient(f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_COLLECTION}")
    db = cluster[db_name]
    collection = db[collection_name]
    collection.insert_many(properties)