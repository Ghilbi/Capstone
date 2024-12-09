# logger_config.py

import logging

def setup_logging():
    """
    Set up logging configuration.
    """
    logging.basicConfig(
        filename='application.log',  # Changed from 'import_errors.log' for comprehensive logging
        level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a'  # Append mode
    )
