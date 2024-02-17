import requests
import streamlit

url = "http://0.0.0.0:12000/api/v1/summarize_video"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
}

json_data = {
    "channels": [],
    "videos": [
        "https://www.youtube.com/watch?v=TRjq7t2Ms5I",
        "https://www.youtube.com/watch?v=JEBDfGqrAUA",
    ],
    "limit_transcript": 0.25,
    "top_n": 2,
    "sort_by": "newest",
}

resp = requests.post(
    url,
    headers=headers,
    json=json_data,
)


def print_response(response):
    content = response.json()
    summaries = content.get("data").get("summaries")
    for summary in summaries:
        for item in summary:
            for k, v in item.items():
                print(f"{k}: {v}")
        print("\n")
