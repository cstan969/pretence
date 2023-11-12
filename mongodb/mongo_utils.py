from pymongo import MongoClient
from datetime import datetime

DB_NAME='pretence2'
# DB_NAME='pretence2-test'
# import os
# if os.getenv('db_env') == "test":
#     DB_NAME='pretence2-test'
URI="mongodb://localhost:27017"

def get_current_datetime_as_string():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_mongo_client():
    return MongoClient(URI)

    
def upsert_item(collection_name, item):
        """
        Upsert an item in the MongoDB collection.
        If the item exists, it will be updated. Otherwise, a new document will be inserted.
        """
        try:
            client = MongoClient(URI)
            db = client[DB_NAME]
            collection = db[collection_name]
            item['last_updated'] = get_current_datetime_as_string()
            query = {'_id': item['_id']}
            collection.update_one(query, {'$set': item}, upsert=True)
            return item
        finally:
            client.close()

# Utility function for querying a collection
def query_collection(collection_name, query):
    try:
        client = MongoClient(URI)
        db = client[DB_NAME]
        collection = db[collection_name]
        return list(collection.find(query))
    finally:
        # Close the connection
        client.close()

def delete_items(collection_name:str,query:dict):
    try:
        client = MongoClient(URI)
        db = client[DB_NAME]
        collection = db[collection_name]
        collection.delete_many(query)
    finally:
        client.close()

def get_current_date_formatted_no_spaces():
    now = datetime.now()
    formatted_date = now.strftime("%Y%m%d%H%M%S%f")
    return formatted_date