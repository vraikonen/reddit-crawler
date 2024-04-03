import json
import sys
import logging
from utils.logging import logging_crawler, custom_exception_hook
from modules.dump_query import read_lines_zst, RedditArchiveQuery
from utils.reading_config import reading_config_database, reading_query_config
from utils.mongodb_writer import initialize_mongodb, write_data

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
        f"Connection established with: {server_path}; Database name:{database}; Collection name: {collection1} "
    )

    # Get query config
    path_to_query_config = "config/query-params.ini"
    (
        keywords,
        author,
        subreddit,
        start_date,
        end_date,
        sub_dump_file_path,
        com_dump_file_path,
    ) = reading_query_config(path_to_query_config)
    # Initialize query object
    query = RedditArchiveQuery(keywords, author, start_date, end_date, subreddit)

    file_lines = 0
    bad_lines = 0
    # Iterate over the dump folder
    logging.info(f"=== Processing submissions from the dump ===")
    for line, file_bytes_processed in read_lines_zst(sub_dump_file_path):
        # Apply query and write data
        created_at, obj = query.apply_query(line=line)

        # Track bad lines and timestamps
        if created_at == None:
            bad_lines += 1
            continue
        file_lines += 1
        if file_lines % 100000 == 0:
            logging.info(
                f"{created_at.strftime('%Y-%m-%d %H:%M:%S')}; Processed lines: {file_lines:,}; Bad lines: {bad_lines:,}"
            )
        # Check if subission is in specified interval
        if start_date is not None and start_date > created_at:
            continue
        # Terminate script if end_date is passed
        if end_date is not None and end_date < created_at:
            logging.info(
                f"We have reached our end date. Last timestamp: {created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            break
        # Write data
        if obj is not None:
            write_data(obj, submissions_dump_collection)
    logging.info(
        f"Submissions processing complete. Processed lines: {file_lines:,}; Bad lines: {bad_lines:,}"
    )

    # Get filtered submissions
    cursor = submissions_dump_collection.find({})
    submissions_ids = []
    for doc in cursor:
        the_id = doc.get("id")
        submissions_ids.append(the_id)
    sub_set = set(submissions_ids)

    # Get comments from the dump associated with the filtered submissions
    logging.info("=" * 50)
    logging.info(
        f"Connection established with: {server_path}; Database name:{database}; Collection name: {collection2} "
    )
    logging.info(f"=== Processing comments from the dump ===")

    processed_lines = 0
    num_com = 0
    bad_line = 0

    # Iterate over the dump folder
    for line, file_bytes_processed in read_lines_zst(com_dump_file_path):
        try:
            obj = json.loads(line)
            processed_lines += 1
        except (KeyError, json.JSONDecodeError) as e:
            logging.error(f"Error decoding JSON: {e}")
            bad_lines += 1
        # Get the id of the submission associated with the comment
        link_id = obj["link_id"]
        sub_id = link_id[3:]
        # Check if the comment belong to the filtered submissions
        if sub_id in sub_set:
            num_com += 1
            write_data(obj, comments_dump_collection)
        if processed_lines % 100000 == 0:
            logging.info(
                f"Processed comments lines: {processed_lines:,}; Bad comments lines: {bad_lines:,}"
            )

    logging.info(
        f"Comments processing complete. Processed lines: {processed_lines:,}; Bad lines: {bad_lines:,}"
    )
