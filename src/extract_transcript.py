"""Extract transcript from a YouTube video"""

# provide youtube url
# get the video id from the url
# extract transctipt from youtube video as text file
# if the transcript is not in english, translate it
# save text as file with naming convention: channel_name-video_name
# summarize text using an open source model from hugging face

import json
import urllib.parse
import urllib.request
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


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


def save_trancript(transcript: list[str], video_id: str, file_dir: Path) -> None:
    """Saves a transcript to a location"""

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    video_title = get_video_title(video_url)
    file_path = file_dir / video_title
    file_path = f"{file_path}.txt"

    if not file_dir.exists():
        file_dir.mkdir()

    with open(file_path, mode="w") as f:
        f.writelines(transcript)


def convert_video_ts(s: float) -> str:
    """Converts a video time stamp in secs to H:M:S"""

    hour, remainder_secs = divmod(s, 3600)
    minutes, secs = divmod(remainder_secs, 60)

    hour = int(hour)
    minutes = str(int(minutes)).zfill(2)
    secs = str(int(secs)).zfill(2)

    res = f"{hour}:{minutes}:{secs}"
    return res


def main(url: str, dir: Path):
    video_id = get_video_id(url)
    transcript = get_video_transcript(video_id)
    save_trancript(transcript, video_id, dir)


if __name__ == "__main__":
    from params import transcript_dir

    URL = "https://www.youtube.com/watch?v=JEBDfGqrAUA"
    main(URL, transcript_dir)
