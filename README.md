# Property Webscraper

This is a simple toolkit to webscrape property data from Rightmove and store it in a MongoDB collection. 

## Installatin

Clone the repo, create your environment and run `pip install -r requirements.txt`. 

Next, you'll need to create an `.env` file and include the following information:

```
MONGO_USER=<your mongoDB username>
MONGO_PASSWORD=<your mongoDB password>
MONGO_CLUSTER=<the mongoDB cluster string>
MONGO_DB_NAME=<the mongoDB database name>
MONGO_COLLECTION=<the mongoDB collection>
```

For example, for the connection string `mongodb+srv://JordanSmith:<password>@cluster-test.fndbj.mongodb.net/myFirstDatabase`, your `.env` file would be as follows:

```
MONGO_USER="JordanSmith"
MONGO_PASSWORD=<password>
MONGO_CLUSTER="cluster-test.fndbj.mongodb.net"
MONGO_DB_NAME="myFirstDatabase"
MONGO_COLLECTION=<the mongoDB collection>
```

See [https://medium.com/analytics-vidhya/connecting-to-mongodb-atlas-with-python-pymongo-5b25dab3ac53](this Medium article) for more guidance.


## Running

Just run `python run.py` to launch the webscraper. Property data will be scraped for each location code provided in `location_codes.json`. 

This will save all scraped property data to your MongoDB collection, and save local copies for each location in a `json_data/` directory. 


## Data

This toolkit is simple but powerful, and scrapes a large amount of data per property. Some is useful, some is not. 

Here is an overview:

| Syntax      | Description |
| ----------- | ----------- |
| _id         | Unique Rightmove property ID  (str)      |
| id          | Unique Rightmove property ID  (str)     |
| bedrooms   | Number of bedrooms (int)       |
| bathrooms   | Number of bathrooms (int)       |
| numberOfImages   | Number of images associated with property (int)       |
| numberofFloorplans   | Number of floorplan images associated with property (int)        |




## To Do
* Add optional arguments for `save_locally=False` and `num_pages=X`
* Add more property codes


