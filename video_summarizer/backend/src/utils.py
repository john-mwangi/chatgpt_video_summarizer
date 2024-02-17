import logging
import os
from urllib.parse import quote_plus

from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient

load_dotenv()
app_env = os.environ.get("APP_ENV")
env_file = f"{app_env}.env"
load_dotenv(find_dotenv(filename=env_file))


def get_mongodb_client():
    """Establishes a MongoDB client

    Returns
    ---
    Tuple of (MongoClient, database_name)
    """

    _USER = os.environ.get("_MONGO_UNAME")
    _PASSWORD = quote_plus(os.environ.get("_MONGO_PWD"))
    _HOST = os.environ.get("_MONGO_HOST")
    _DB = os.environ.get("_MONGO_DB")
    _PORT = os.environ.get("_MONGO_PORT")

    uri = f"mongodb://{_USER}:{_PASSWORD}@{_HOST}:{_PORT}/?authSource={_DB}"

    return MongoClient(uri), _DB


def get_logging_level():
    level = os.environ.get("LOGGING_LEVEL", "WARNING")
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    print("Logging level:", level)
    return levels.get(level)


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=get_logging_level(),
)
logger = logging.getLogger()

if __name__ == "__main__":
    logger.debug("this is debug")
    logger.info("this is info")
    logger.warning("this is warn")
