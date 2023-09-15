import json

with open('image_classification/no_exterior.json', 'r') as f:
    no_facade = json.load(f)

print(len(no_facade))