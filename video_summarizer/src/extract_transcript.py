"""Extract transcript from a YouTube video"""

import json
import urllib.parse
import urllib.request

from youtube_transcript_api import YouTubeTranscriptApi

from video_summarizer.src.utils import get_mongodb_client


def get_video_id(url: str) -> str:
    """Extracts the YouTube video id from the url"""

    return url.split("?v=", 1)[-1]


def get_video_transcript(video_id: str) -> list[str]:
    """Extract video transcript and save as text file"""

    yt = YouTubeTranscriptApi()
    transcript = yt.get_transcript(video_id)

    tr = []
    for i in transcript:
        t = i.get("text")
        s = i.get("start")
        ts = convert_video_ts(s)
        tr.append(f"\n{ts} - {t}")

    return tr


def get_video_title(video_url: str) -> str:
    """Get the title of a YouTube video"""

    params = {"format": "json", "url": video_url}
    base_url = "https://www.youtube.com/oembed"
    query_str = urllib.parse.urlencode(params)
    url = base_url + "?" + query_str

    with urllib.request.urlopen(url) as response:
        resp_txt = response.read()
        data = json.loads(resp_txt.decode())

    return data.get("title", "Unknown Video Title")


def save_trancript(transcript: list[str], video_id: str) -> None:
    """Saves a transcript to the database"""

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    video_title = get_video_title(video_url)

    data = {
        "video_id": video_id,
        "video_url": video_url,
        "video_title": video_title,
        "transcript": transcript,
    }

    client, db = get_mongodb_client()

    with client:
        db = client[db]
        transcripts = db.transcripts
        result = transcripts.insert_one(data)

    print(f"Successfully saved to the database: {result.inserted_id}")


def convert_video_ts(s: float) -> str:
    """Converts a video time stamp in secs to H:M:S"""

    hour, remainder_secs = divmod(s, 3600)
    mins, secs = divmod(remainder_secs, 60)

    hour = int(hour)
    minutes = str(int(mins)).zfill(2)
    seconds = str(int(secs)).zfill(2)

    res = f"{hour}:{minutes}:{seconds}"
    return res


def get_transcript_from_db(video_id: str):
    client, db = get_mongodb_client()
    with client:
        db = client[db]
        transcripts = db.transcripts
        result = transcripts.find_one({"video_id": video_id})

    return result


def main(url: str):
    video_id = get_video_id(url)
    result = get_transcript_from_db(video_id)

    if result is not None:
        print(f"{video_id=} transcript has already been downloaded")
    else:
        transcript = get_video_transcript(video_id)
        save_trancript(transcript, video_id)

    return video_id


if __name__ == "__main__":
    URL = "https://www.youtube.com/watch?v=JEBDfGqrAUA"
    main(URL)
