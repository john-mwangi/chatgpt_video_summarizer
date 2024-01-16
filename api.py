from fastapi import FastAPI
from pydantic import BaseModel

from main import main


class VideoUrls(BaseModel):
    channels: list[str]
    videos: list[str]
    limit_transcript: float | int | None = 0.25
    top_n: int = 2
    sort_by: str = "newest"


app = FastAPI()


@app.post(path="/summarize_video")
def fetch_video_summary(video_urls: VideoUrls):
    summaries = main(
        channels=video_urls.channels,
        videos=video_urls.videos,
        LIMIT_TRANSCRIPT=video_urls.limit_transcript,
        sort_by=video_urls.sort_by,
    )

    data = {"summaries": summaries}

    return {
        "data": data,
        "status": "SUCCESS",
        "message": "Video was successfully summarised",
    }
