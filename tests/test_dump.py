# just check if the things that are returned are the ones you queried (check if the date fits, keywords, etc)
# Do two times the same shit and assert results
import pytest
import json
from pymongo import MongoClient
from datetime import datetime
from modules.dump_query import RedditArchiveQuery


def test_query():
    dummy_submissions = [
        {
            "title": "German Floods in Berghaim",
            "selftext": "Check out how wild this river is!",
            "subreddit": "germany",
        },
        {"title": "OMG!!", "selftext": "", "subreddit": "rhein"},
        {
            "title": "Check this high water?! #flooding",
            "selftext": "Crazy",
            "subreddit": "germany",
        },
        {
            "title": "England won the world cup!",
            "selftext": "50 years ago :(",
            "subreddit": "funny",
        },
    ]
    keywords = ["flood", "rhein"]
    author = None
    start_date = None
    end_date = None
    subreddit = "Rhein"
    # Check if the filtering is right
    query = RedditArchiveQuery(keywords, author, start_date, end_date, subreddit)
    titles = []
    selftexts = []
    for line in dummy_submissions:
        line = json.dumps(line)
        created_at, obj = query.apply_query(line)
        if obj:
            titles.append(obj["title"])
            selftexts.append(obj["selftext"])

    # Define expected titles and selftexts based on the dummy submissions
    expected_titles = [
        "German Floods in Berghaim",
        "OMG!!",
        "Check this high water?! #flooding",
    ]
    expected_selftexts = ["Check out how wild this river is!", "", "Crazy"]

    # Assert that the titles and selftexts extracted from dummy submissions match the expected values
    assert titles == expected_titles
    assert expected_selftexts == selftexts


def test_date_dump():
    # In my config, I decided to use these start and end date
    # Now checking if my data is in this period
    start_date = datetime(2021, 7, 10, 0, 0, 0)
    end_date = datetime(2021, 7, 20, 0, 0, 0)
    # Connect to MongoDB
    client = MongoClient("localhost", 27017)
    db = client["Reddit-Germany-Floods"]
    collection = db["submissions_dump"]

    documents = collection.find()
    created_at_list = [
        datetime.utcfromtimestamp(doc.get("created_utc"))
        for doc in documents
        if "created_utc" in doc
    ]
    for item in created_at_list:
        assert item >= start_date and item <= end_date
