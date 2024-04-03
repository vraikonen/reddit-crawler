# Check if the attribtues returned from the API are the same as those found in the dump
# Do two times the same shit and assert results
import pytest
from pymongo import MongoClient

from utils.reading_config import reading_config_reddit
from modules.reddit_api import initilize_reddit


# Explore if the reposne is always the same
def test_check_response():

    # Read Reddit API config
    config_file = "config/config-reddit-api.ini"
    (
        client_id,
        client_secret,
        password,
        username,
        user_agent,
        submission_attributes,
        comment_attributes,
    ) = reading_config_reddit(config_file)
    reddit = initilize_reddit(client_id, client_secret, password, username, user_agent)

    # Connect to MongoDB
    client = MongoClient("localhost", 27017)
    db = client["Reddit-Germany-Floods"]
    collection = db["submissions_dump"]

    #############
    # Get IDs of filtered submissions
    sub_ids = []
    cursor = collection.find().limit(5)
    for document in cursor:
        # Get id of the submission
        sub_id = document.get("id")
        sub_ids.append(sub_id)

    # Iterate over each submission and get its attributes from Reddit API
    subs_list1 = []
    for sub_id in sub_ids:
        # Dictionary for submission attributes
        retrieved_sub = {}
        submission = reddit.submission(id=sub_id)
        if submission:
            for item in submission_attributes:
                # Get attributes from the submission
                attribute_value = getattr(submission, item, None)
                retrieved_sub.update({item: str(attribute_value)})
    subs_list1.append(retrieved_sub)

    #############
    # Get IDs of filtered submissions
    sub_ids = []
    cursor = collection.find().limit(5)
    for document in cursor:
        # Get id of the submission
        sub_id = document.get("id")
        sub_ids.append(sub_id)
    # Iterate over each submission and get its attributes from Reddit API
    subs_list2 = []
    for sub_id in sub_ids:
        # Dictionary for submission attributes
        retrieved_sub = {}
        submission = reddit.submission(id=sub_id)
        if submission:
            for item in submission_attributes:
                # Get attributes from the submission
                attribute_value = getattr(submission, item, None)
                retrieved_sub.update({item: str(attribute_value)})
    subs_list2.append(retrieved_sub)

    assert subs_list2 == subs_list1
