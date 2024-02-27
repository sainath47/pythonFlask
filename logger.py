import sys
import os
import logging

def configure_logging(log_directory):
    # Ensure that the log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a file handler
    file_handler = logging.FileHandler(filename=os.path.join(log_directory, 'app.log'), mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Optionally, add a console handler for displaying logs in the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Redirect stdout to the logging system
    sys.stdout = file_handler.stream