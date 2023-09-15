import os
import json
import time
import logging
import requests
import bson.json_util as json_util
from tqdm import tqdm
from skimage import io
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid

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

sample = collection.aggregate([{ "$sample": { "size": 10 } }])

# Model: https://huggingface.co/andupets/real-estate-image-classification-30classes
API_URL = "https://api-inference.huggingface.co/models/andupets/real-estate-image-classification-30classes"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def query(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        data = response.content
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()
    else:
        print(f"Failed to fetch image from URL: {image_url}")
        return None


current_timestamp = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

if not os.path.exists('image_classification/'):
    os.mkdir('image_classifiation/')
    with open('image_classification/no_exterior.json', 'w') as json_file:
        json.dump([], json_file)

os.mkdir(f'image_classification/{current_timestamp}')

with open('image_classification/no_exterior.json', 'r') as f:
  no_exterior = json.load(f)

for prop_record in sample:
    impreds = []
    prop_id = prop_record['id']
    print(f'Processing property {prop_id}')
    image_urls = [im['url'] for im in prop_record['images']]

    num_images = len(image_urls)
    num_columns = 5
    num_rows = -(-num_images // num_columns)

    fig = plt.figure(figsize=(15, 3 * num_rows)) 
    grid = ImageGrid(fig, 111, nrows_ncols=(num_rows, num_columns), axes_pad=0.5)

    for idx, url in enumerate(image_urls):
        imscores = query(url)

        if not imscores:
            print(f'Unable to retrieve {url}')
            continue

        if not isinstance(imscores, list):
            print('ERROR:', imscores)
            if "estimated_time" in imscores.keys():
                print(f'Sleeping for {imscores["estimated_time"]} seconds')
                time.sleep(imscores['estimated_time'])
                continue
            break
            

        scores = [pred['score'] for pred in imscores]
        max_ix = scores.index(max(scores))
        pred_label = imscores[max_ix]['label']

        impreds.append(pred_label)

        image = io.imread(url)
        ax = grid[idx]
        ax.imshow(image)
        ax.set_title(f'Prediction: {pred_label}\nScore: {imscores[max_ix]["score"]}', fontsize=10)
        ax.axis('off')

    if 'facade' not in str(set(impreds)):
        print(f'It looks like {prop_id} does not contain an exterior picture')
        no_exterior.append(prop_id)

    plt.tight_layout()
    output_file = f"image_classification/{current_timestamp}/{prop_id}_predictions.png"
    plt.savefig(output_file)

no_exterior = list(set(no_exterior))

with open('image_classification/no_exterior.json', 'w') as json_file:
  json.dump(no_exterior, json_file)
