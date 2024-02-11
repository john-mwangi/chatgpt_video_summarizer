import os
from urllib.parse import quote_plus

from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient


def get_mongodb_client():
    """Establishes a MongoDB client

    Returns
    ---
    Tuple of (MongoClient, database_name)
    """

    load_dotenv()
    app_env = os.environ.get("APP_ENV")
    env_file = f"{app_env}.env"

    load_dotenv(find_dotenv(filename=env_file))

    _USER = os.environ.get("_MONGO_UNAME")
    _PASSWORD = quote_plus(os.environ.get("_MONGO_PWD"))
    _HOST = os.environ.get("_MONGO_HOST")
    _DB = os.environ.get("_MONGO_DB")
    _PORT = os.environ.get("_MONGO_PORT")

    uri = f"mongodb://{_USER}:{_PASSWORD}@{_HOST}:{_PORT}/?authSource={_DB}"

    return MongoClient(uri), _DB
