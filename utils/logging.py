import logging
import sys


def logging_crawler():
    """
    Configures logging for the application and sets up a StreamHandler for console output.

    The function configures the logging system with a file handler and a StreamHandler. The file handler
    writes log entries to a file named 'applicationMain.log', and the StreamHandler prints log entries to
    the console. The console output is limited to errors.

    Note: This function should be called at the beginning of the application.

    Returns:
    None
    """
    logging.basicConfig(
        filename="applicationMain.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s  [%(filename)s:%(funcName)s]",
        level=logging.INFO,
    )
    # Create a StreamHandler to also print log entries to the console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)  # Set the level for console output
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s  [%(filename)s:%(funcName)s]"
    )
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    logging.getLogger().addHandler(console_handler)
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)


def custom_exception_hook(exc_type, exc_value, exc_traceback):
    """
    Logs unhandled exceptions with detailed information.

    This function is intended to be used as a custom exception hook to log unhandled exceptions. It logs
    the exception type, value, and traceback at the ERROR level.

    Parameters:
    - exc_type (type): The type of the exception.
    - exc_value (Exception): The exception instance.
    - exc_traceback (traceback): The traceback object.

    Returns:
    None
    """
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
