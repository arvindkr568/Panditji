import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Configures a centralized logger for the Pandit Ji Engine.
    Logs are printed to the console and saved to logs/panditji.log.
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "panditji.log")

    # Create a custom logger
    logger = logging.getLogger("PanditJiEngine")
    
    # If the logger already has handlers (e.g. during Flask reloads), do not add them again
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG) # Capture all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    import pytz
    from datetime import datetime
    
    class ISTFormatter(logging.Formatter):
        def converter(self, timestamp):
            dt = datetime.fromtimestamp(timestamp, tz=pytz.timezone('Asia/Kolkata'))
            return dt.timetuple()

    # Define a rich format for the logs using IST
    formatter = ISTFormatter(
        fmt="[%(asctime)s IST] [%(levelname)s] [%(module)s:%(funcName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler (Prints to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Keep console clean with INFO and above
    console_handler.setFormatter(formatter)

    # File Handler (Saves to logs/panditji.log, max 5MB per file, keeps 3 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Save everything to the file for deep debugging
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Global instance to be imported by all modules
logger = setup_logger()
