import asyncio
import re
import logging
import pymongo


def initialize_mongodb(
    server_path,
    database,
    collection1,
    collection2,
    collection3,
    collection4,
    collection5,
):
    """
    Initializes a connection to a MongoDB server and returns specified collections.

    This function establishes a connection to a MongoDB server, accesses/creates a database named 'database',
    as well as accesses/creates five collections.

    Parameters are located in config file.

    Parameters:
    - server_path (str): The MongoDB server path.
    - database (str): The name of the MongoDB database.
    - collection1 (str): The name of the first collection.
    - collection2 (str): The name of the second collection.
    - collection3 (str): The name of the third collection.
    - collection4 (str): The name of the fourth collection.
    - collection5 (str): The name of the fifth collection.


    Returns:
    tuple: A tuple containing the specified MongoDB collections (collection1 to collection5).
    """
    # Initialize the MongoDB client
    myclient = pymongo.MongoClient(server_path)

    # Access or create the database
    db = myclient[database]

    # Access or create the collections
    collection1 = db[collection1]
    collection2 = db[collection2]
    collection3 = db[collection3]
    collection4 = db[collection4]
    collection5 = db[collection5]

    # Return the collections
    return collection1, collection2, collection3, collection4, collection5


# Define an asynchronous lock
lock = asyncio.Lock()


# Writing in the database
def write_data(data, collection_name):
    """
    Writes data to a MongoDB collection in an asynchronous manner.

    This asynchronous function writes data to the specified MongoDB collection in a safe and
    thread-safe manner using an asynchronous lock. The 'data' parameter should be a dictionary
    or a list of dictionaries.

    Parameters:
    - data: The data to be written to the MongoDB collection.
    - collection_name: The MongoDB collection to write data to.

    Returns:
    None
    """
    try:
        # async with lock:
        # Insert the data into the collection
        # Data should be a dictionary or a list of dictionaries
        if isinstance(data, dict):
            # Insert a single document
            collection_name.insert_one(data)
        elif isinstance(data, list):
            # Insert multiple documents
            collection_name.insert_many(data)
        else:
            logging.info(
                f"Probably wrong data type, it should be dictionary or list of dictionaries!"
            )
    except Exception as e:
        logging.error(f"An error occurred for write_data(): {str(e)}")


# Creating indeces
def create_index(collection, index):
    """
    Creates an index in a MongoDB collection.

    This function creates an index in the specified MongoDB collection using the provided 'index'.
    The 'index' parameter should be a dictionary defining the fields and their ordering for the index.

    Parameters:
    - collection: The MongoDB collection in which the index will be created.
    - index: A dictionary specifying the fields and ordering for the index.

    Returns:
    None
    """
    try:
        collection.create_index(index, unique=False)
    except Exception as e:
        logging.error(f"Error creating index in {collection}: {str(e)}")
