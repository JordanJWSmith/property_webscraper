import json
import pandas as pd
import numpy as np

from tqdm import tqdm
from transformers import pipeline
from PIL import UnidentifiedImageError


pipe = pipeline("image-classification", model="andupets/real-estate-image-classification-30classes")

with open('json_data/wandsworth.json') as f:
  wandsworth = json.load(f)


ITEMS = []
for listing in tqdm(wandsworth[:200]):
  _id = listing['id']
  price = listing['price']['amount']
  bedrooms = listing['bedrooms']
  bathrooms = listing['bathrooms']
  summary = listing['summary']
  text = listing['text']['description']
  latitude = listing['location']['latitude']
  longitude = listing['location']['longitude']
  property_type = listing['propertySubType']
  lease = listing['tenure']['tenureType']

  for image in listing['images']:
    image_url = image['url']

    ITEMS.append([_id, price, bedrooms, bathrooms, summary, text, latitude, longitude, property_type, lease, image_url])

wandsworth_df = pd.DataFrame(ITEMS)
wandsworth_df.columns = ['_id', 'price', 'bedrooms', 'bathrooms', 'summary', 'text', 'latitude', 'longitude', 'property_type', 'lease', 'image_url']

image_labels = []
for image_url in tqdm(wandsworth_df['image_url'].tolist()):
  try:
      # find the top scoring class for each image
      result = pipe(image_url, top_k=1)
      score = result[0]['score']
      label = result[0]['label']
  except UnidentifiedImageError: 
      score, label = np.nan, np.nan

  image_labels.append(label)

wandsworth_df['image_label'] = image_labels
wandsworth_df.to_csv('wandsworth_200.csv')