import configparser
import os
from datetime import datetime, timezone
import ast


def reading_query_config(config_path):
    """
    Reads configuration values from a Telegram config file.

    Parameters:
    - path(str) to Config file

    Returns:
    tuple: A tuple containing the following configuration values:
        - keywords (list).
        - author (str).
        - subreddit (str).
        - start_date (datetime object).
        - end_date (datetime object)
    """
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_path)
    keywords = config["Query"]["keywords"]
    author = config["Query"]["author"]
    subreddit = config["Query"]["subreddit"]
    start_date = config["Query"]["start_date"]
    end_date = config["Query"]["end_date"]
    file_path_sub = config["Query"]["file_path_sub"]
    file_path_com = config["Query"]["file_path_com"]
    # Make them all None if None
    if keywords == "None":
        keywords = None
    else:
        keywords = ast.literal_eval(keywords)

    if author == "None":
        author = None
    else:
        author = ast.literal_eval(author)

    if subreddit == "None":
        subreddit = None
    else:
        subreddit = ast.literal_eval(subreddit)

    if start_date == "None":
        start_date = None
    else:
        start_date_naive = datetime.strptime(start_date, "%Y, %m, %d, %H, %M, %S")
        start_date = start_date_naive.replace(tzinfo=timezone.utc)

    if end_date == "None":
        end_date = None
    else:
        end_date_naive = datetime.strptime(end_date, "%Y, %m, %d, %H, %M, %S")
        end_date = end_date_naive.replace(tzinfo=timezone.utc)

    return (
        keywords,
        author,
        subreddit,
        start_date,
        end_date,
        file_path_sub,
        file_path_com,
    )


def reading_config_database(config_file):
    """
    Reads database configuration values from a database config file.

    Reads the specified configuration file and extracts the server path,
    database name, and collection names.

    Parameters:
    - config_file (str): The path to the database config file.

    Returns:
    tuple: A tuple containing the following configuration values:
        - server_path (str): The server path for the database.
        - database (str): The name of the database.
        - collection1 (str): Name of the first collection.
        - collection2 (str): Name of the second collection.
        - collection3 (str): Name of the third collection.
        - collection4 (str): Name of the fourth collection.
        - collection5 (str): Name of the fifth collection.
    """
    # Reading Configs
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_file)

    # Setting configuration values
    server_path = config["Database"]["server_path"]

    database = config["Database"]["database"]

    collection1 = config["Database"]["collection1"]
    collection2 = config["Database"]["collection2"]
    collection3 = config["Database"]["collection3"]
    collection4 = config["Database"]["collection4"]
    collection5 = config["Database"]["collection5"]

    return (
        server_path,
        database,
        collection1,
        collection2,
        collection3,
        collection4,
        collection5,
    )


def reading_config_reddit(config_file):
    """
    Initializes Reddit client based on configuration file.

    Reads the configuration file specified by 'config_file' and extracts the necessary
    parameters to initialize a Reddit client.

    Parameters:
    - config_file (str): The path to the configuration file.

    Returns:
    tuple: A tuple containing:
        - str: The client ID for Reddit.
        - str: The client secret for Reddit.
        - str: The password associated with the Reddit account.
        - str: The username of the Reddit account.
        - str: The user agent for Reddit API requests.
        - list: A list of attributes to extract from Reddit submissions.
        - list: A list of attributes to extract from Reddit comments.
    """
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_file)
    client_id = config["Reddit"]["client_id"]
    client_secret = config["Reddit"]["client_secret"]
    password = config["Reddit"]["password"]
    username = config["Reddit"]["username"]
    user_agent = config["Reddit"]["user_agent"]
    submission_attributes = config["Reddit"]["submission_attributes"]
    submission_attributes = ast.literal_eval(submission_attributes)
    comment_attributes = config["Reddit"]["comment_attributes"]
    comment_attributes = ast.literal_eval(comment_attributes)

    return (
        client_id,
        client_secret,
        password,
        username,
        user_agent,
        submission_attributes,
        comment_attributes,
    )
