# Property Webscraper

This is a simple toolkit to webscrape property data from Rightmove and store it in a MongoDB collection. 

## Installation

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

See [this Medium article](https://medium.com/analytics-vidhya/connecting-to-mongodb-atlas-with-python-pymongo-5b25dab3ac53) for more guidance.


## Running

Just run `python run.py` to launch the webscraper. Property data will be scraped for each location code provided in `location_codes.json`. 

This will save all scraped property data to your MongoDB collection, and save local copies for each location in a `json_data/` directory. 


## Data

This toolkit is simple but powerful, and scrapes a large amount of data per property in nested JSON format. Some elements are useful, some are not. 

Here is an overview:

| Syntax      | Description | Type |
| ----------- | ----------- | ---- |
| _id         | Unique Rightmove property ID  (str)      | str |
| id          | Unique Rightmove property ID  (str)     | str |
| bedrooms   | Number of bedrooms (int)       | int |
| bathrooms   | Number of bathrooms (int)       | int |
| numberOfImages   | Number of images associated with property (int)       | int |
| numberofFloorplans   | Number of floorplan images associated with property (int)        | int |
| numberofFloorplans   | Number of floorplan images associated with property (int)        | int |
| summary   | Written summary of the property (str)       | str |
| displayAddress   | A truncated address, usually street and postcode (str)        | str |
| countryCode   | A code to indicate the country, i.e. "GB"        | str |
| location   | An object containing location information including latitude and longitude  | obj |
| propertyImages   | An object containing image URLs for each property image. Also separate objects for the main image and main map image.    | obj |
| propertySubType   | The type of property, i.e. "Apartment"    | str |
| listingUpdate   | Object containing the reason and date a property was reduced   | obj |
| premiumListing   | Whether or not the property is a premium listing.    | bool |
|  featuredProperty   | Whether or not the property is a featured listing.    | bool |
|  price   | An object containing the price, frequency and currencycode    | obj |
|  customer   | An object containing information on the estate agent listing the property, including name, address and branch   | obj | 
| distance | An object to signify distance | ? |
| transactionType | What type of transaction this is, i.e. "BUY", "LET" | str | 
| productLabel | An object describing a prdoduct label | obj | 
| commercial | Whether the property is suitable for commercial use | bool | 
| development | Whether the property is suitable for development | bool | 
| residential | Whether the property is residential | bool | 
| students | Whether the property is student accommodation | bool | 

...and 65 other fields (document still in progress)




## To Do
* Add optional arguments for `save_locally=False` and `num_pages=X`
* Add more property codes
* Review/complete data in above table
* Add feature to convert to CSV


