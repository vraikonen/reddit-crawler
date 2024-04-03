import json
import pickle

from datetime import date, datetime


# Functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Saving data into json
def save_level_data(level_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_level_data.json"

    with open(filename, "w") as outfile:
        json.dump(level_data, outfile, cls=DateTimeEncoder)


# Reading input channels
def read_channels_from_file(file_path):
    """
    Reads input channels from a text file.

    This function reads the content of a text file located at the specified 'file_path'.
    Each line in the file is treated as a separate input channel, and the function returns
    a list of channels after stripping leading and trailing whitespaces.

    Parameters:
    - file_path (str): The path to the input channels file.

    Returns:
    list: A list of input channels read from the file.
    """
    with open(file_path, "r") as file:
        return [line.strip() for line in file]


# Write pickle
def write_pickle(data, file_path):
    """
    Writes data to a pickle file.

    Parameters:
    - data: The data to be written to the pickle file.
    - file_path (str): The path to the output pickle file.

    Returns:
    None
    """
    with open(file_path, "wb") as file:
        pickle.dump(data, file)


# Read pickle
def read_pickle(file_path):
    """
    Reads data from a pickle file.

    Parameters:
    - file_path (str): The path to the input pickle file.

    Returns:
    The deserialized data read from the pickle file.
    """
    with open(file_path, "rb") as file:
        data = pickle.load(file)
    return data
