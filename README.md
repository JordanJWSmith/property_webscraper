# Property Webscraper

This is a simple toolkit to webscrape property data from Rightmove and store it in a MongoDB collection. 

## Deployment

Clone the repo, create your environment and run `pip install -r requirements.txt`. 

Next, you'll need to create an `.env` file and include the following information:

```
MONGO_USER=<your mongoDB username>
MONGO_PASSWORD=<your mongoDB password>
MONGO_CLUSTER=<the mongoDB cluster string>
MONGO_DB_NAME="<the mongoDB database name>
MONGO_COLLECTION=<the mongoDB collection>
```