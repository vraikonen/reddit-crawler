import zstandard
import os
import json
import logging.handlers
import re
from datetime import datetime, timezone


def read_and_decode(
    reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0
):
    """
    Read and decode data from a zstandard-compressed file.

    Parameters:
    - reader: Zstandard reader object.
    - chunk_size (int): Size of the chunk to be read and decoded.
    - max_window_size (int): Maximum window size for decoding.
    - previous_chunk (str, optional): Previously read chunk for decoding continuation.
    - bytes_read (int, optional): Total bytes read.

    Returns:
    str: Decoded chunk of data.
    """

    chunk = reader.read(chunk_size)
    bytes_read += chunk_size
    if previous_chunk is not None:
        chunk = previous_chunk + chunk
    try:
        return chunk.decode()
    except UnicodeDecodeError:
        if bytes_read > max_window_size:
            raise UnicodeError(
                f"Unable to decode frame after reading {bytes_read:,} bytes"
            )
        # log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
        return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
    with open(file_name, "rb") as file_handle:
        buffer = ""
        reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(
            file_handle
        )
        while True:
            chunk = read_and_decode(reader, 2**27, (2**29) * 2)

            if not chunk:
                break
            lines = (buffer + chunk).split("\n")

            for line in lines[:-1]:
                yield line, file_handle.tell()

            buffer = lines[-1]

        reader.close()


def check_and_save_json(line, keywords, output_file, created):
    try:
        obj = json.loads(line)
    except (KeyError, json.JSONDecodeError) as err:
        logging.error(f"Error decoding JSON: {err}")
    created = datetime.utcfromtimestamp(int(obj["created_utc"]))

    # Extract 'selftext' and 'title' fields from the JSON object
    selftext = obj.get("selftext", "")
    title = obj.get("title", "")

    # Combine 'selftext' and 'title' for a comprehensive check
    combined_text = f"{selftext} {title}"

    # Check if any of the keywords associated with floods are present
    if any(re.search(keyword, combined_text, re.IGNORECASE) for keyword in keywords):
        with open(output_file, "a") as output_handle:
            # Save the JSON object to the output file
            json.dump(obj, output_handle)
            output_handle.write("\n")
    return created


class RedditArchiveQuery:
    """
    Represents a query object for filtering Reddit posts based on various criteria.

    Attributes:
    - keywords (list): List of keywords to search for in the post.
    - author (str): Username of the post author.
    - start_date (datetime): Start date for filtering posts.
    - end_date (datetime): End date for filtering posts.
    - subreddit (str): Name of the subreddit.

    Methods:
    - apply_query(line): Apply the query to a Reddit post. Line parameter is loop
    variable when iterating over read_lines_zst().

    Usage:
    Initialize an instance of RedditArchiveQuery with desired query parameters, then use
    the apply_query method to apply the query to each Reddit post and retrieve filtered posts.
    """

    def __init__(
        self, keywords=None, author=None, start_date=None, end_date=None, subreddit=None
    ):
        self.keywords = [kw.lower() for kw in keywords] if keywords else []
        self.author = [au.lower() for au in author] if author else []
        self.start_date = start_date
        self.end_date = end_date
        self.subreddit = [sub.lower() for sub in subreddit] if subreddit else []

    def apply_query(self, line):
        try:
            obj = json.loads(line)
        except (KeyError, json.JSONDecodeError) as e:
            logging.error(f"Error decoding JSON: {e}")
            return None, None

        # Get some attributes from the post
        created_at = datetime.fromtimestamp(
            int(obj.get("created_utc", 0)), timezone.utc
        )
        selftext = obj.get("selftext", "")
        title = obj.get("title", "")
        combined_text = f"{selftext} {title}"

        # Check if any of the conditions are met
        if not any(
            [
                (
                    self.keywords
                    and any(
                        re.search(re.escape(keyword), combined_text, re.IGNORECASE)
                        for keyword in self.keywords
                    )
                ),
                (self.author and obj.get("author", "").lower() in self.author),
                (self.subreddit and obj.get("subreddit", "").lower() in self.subreddit),
            ]
        ):
            return created_at, None  # Skip if none of the conditions are met

        # Return the object if it passes at least one condition
        return created_at, obj
