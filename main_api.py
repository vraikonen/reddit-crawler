import sys
import logging
from utils.logging import logging_crawler, custom_exception_hook
from utils.reading_config import reading_config_database
from utils.mongodb_writer import initialize_mongodb, write_data
import praw, prawcore

from utils.reading_config import reading_config_reddit

from modules.reddit_api import initilize_reddit

if __name__ == "__main__":
    # Initiate logging, set the custom exception hook
    logging_crawler()
    sys.excepthook = custom_exception_hook

    # Read database and script config
    config_database = "config/config-db.ini"
    (
        server_path,
        database,
        collection1,
        collection2,
        collection3,
        collection4,
        collection5,
    ) = reading_config_database(config_database)

    # Connect to database and create database and collections
    (
        submissions_dump_collection,
        comments_dump_collection,
        submissions_api_collection,
        comments_api_collection,
        failed_API_retireval,
    ) = initialize_mongodb(
        server_path,
        database,
        collection1,
        collection2,
        collection3,
        collection4,
        collection5,
    )
    logging.info(
        f"Connection established with: {server_path}; Database name:{database}; Collection name: {collection3} "
    )
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

    # Get all the processed submissions, if any, to not process again
    try:
        processed_subs = []
        cursor = submissions_api_collection.find({})
        for doc in cursor:
            processed_subs.append(doc.get("id"))
        valid_docs = len(
            processed_subs
        )  # Check lenght of the processed to keep track in the log

        cursor = failed_API_retireval.find({})
        for doc in cursor:
            processed_subs.append(doc.get("id"))
    except Exception as e:
        logging.info(f"Could not access processed subs. Error: {str(e)}")

    # Get the number of submissions filtered from the dump
    processed_subs = set(processed_subs)
    total_documents = submissions_dump_collection.count_documents({})
    logging.info(
        f"Total Number of submissions found in the filtered dump: {total_documents:,}. Number of processed submissions in the previous run(s): {len(processed_subs):,}, of which valid: {valid_docs}"
    )

    # Get number of comments
    total_comments = comments_api_collection.count_documents({})

    # Filtered submissions
    cursor = submissions_dump_collection.find({})
    # Count a bit for logging
    retrieved_docs = 0
    sub_ids = []
    # Get IDs of filtered submissions
    for document in cursor:
        # Get id of the submission
        sub_id = document.get("id")
        sub_ids.append(sub_id)

    retrieved_docs = 0
    # Iterate over each submission and get its attributes from Reddit API
    for sub_id in sub_ids:
        retrieved_docs += 1
        if sub_id in processed_subs:
            continue
        # Dictionary for submission attributes
        retrieved_sub = {}
        invalid_sub = False
        try:
            submission = reddit.submission(id=sub_id)
            if submission:
                for item in submission_attributes:
                    # Get attributes from the submission
                    try:
                        attribute_value = getattr(submission, item, None)
                        retrieved_sub.update({item: str(attribute_value)})
                    except Exception as e:
                        logging.info(
                            f"Accessing the attributes of the submission --{sub_id}--. Error due to {str(e)}. Skipping this submission..."
                        )
                        invalid_sub = True
                        write_data(
                            {"id": sub_id, "error": str(e)}, failed_API_retireval
                        )
                        break

                # Break the loop if the submission is invalid
                if invalid_sub:
                    continue

                # Gather the comments
                try:
                    submission.comments.replace_more(limit=None)
                    for comment in submission.comments.list():
                        total_comments += 1
                        retrieved_comment = {}
                        for item in comment_attributes:
                            try:
                                attribute_value = getattr(comment, item, None)
                                retrieved_comment.update({item: str(attribute_value)})
                            except Exception as e:
                                logging.info(
                                    f"Accessing the attribute --{item}-- of the comment in the submmision --{sub_id}-- was unsuccsesfull due to {str(e)}"
                                )
                                retrieved_comment.update({item: str(e)})
                        write_data(retrieved_comment, comments_api_collection)
                except Exception as e:
                    logging.info(
                        f"Encountered error for comment in the submission {sub_id}: {e}"
                    )

                # Write submission data now, in order to access the same submission when the script is terminated during comments retrieval
                write_data(retrieved_sub, submissions_api_collection)
                valid_docs += 1

            # Log progress
            if retrieved_docs % 100 == 0:
                logging.info(
                    f"Number of processed submissions: {retrieved_docs:,}, of which valid(): {valid_docs:,}. Number of retrieved comments: {total_comments:,}"
                )
        except prawcore.exceptions.Forbidden as e:
            logging.info(f"Encountered Forbidden error for submission {sub_id}: {e}")
            write_data({"id": sub_id, "error": str(e)}, failed_API_retireval)
        except Exception as e:
            logging.info(
                f"Encountered an unexpected error for submission {sub_id}: {e}"
            )
            write_data({"id": sub_id, "error": str(e)}, failed_API_retireval)

    logging.info(
        f"We crawled all filtered submissions via offical API! Number of valid submissions retrieved from the API: {valid_docs:,}, out of total documents from the collection {total_documents:,}, or total accessed documents: {retrieved_docs:,}. Number of comments: {total_comments:,}"
    )
