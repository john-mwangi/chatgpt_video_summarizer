"Tests the api endpoints"

import os

import requests
from dotenv import find_dotenv, load_dotenv

from video_summarizer.backend.configs.config import ApiSettings

load_dotenv()

app_env = os.environ.get("APP_ENV")
env_file = f"{app_env}.env"
load_dotenv(find_dotenv(filename=env_file))


endpoint = os.environ.get("ENDPOINT")
uname = os.environ.get("_USERNAME")
pwd = os.environ.get("_PASSWORD")
api_prefix = ApiSettings.load_settings().api_prefix
token_method = ApiSettings.load_settings().token_method

token_url = f"{endpoint}{api_prefix}{token_method}"


def get_access_token(username: str, password: str):
    token_headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    token_json = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    token_response = requests.post(
        url=token_url, headers=token_headers, data=token_json
    )

    return token_response


def test_auth(username: str = uname, password: str = pwd):
    """Tests then authentication/token method"""

    token_response = get_access_token(username, password)
    assert token_response.status_code == 200


def test_endpoint(method: str = "/summarize_video"):
    """Tests the core endpoint's method"""

    token_response = get_access_token(uname, pwd)
    token_data = token_response.json()
    access_token = token_data["access_token"]

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "channels": [],
        "videos": ["https://www.youtube.com/watch?v=TRjq7t2Ms5I"],
        "limit_transcript": 0.25,
        "top_n": 2,
        "sort_by": "newest",
    }

    url = f"{endpoint}{api_prefix}{method}"
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200
