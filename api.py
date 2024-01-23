import yaml
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from main import main
from src.configs import params_path, statuses


class VideoUrls(BaseModel):
    channels: list[str]
    videos: list[str]
    limit_transcript: float | int | None = 0.25
    top_n: int = 2
    sort_by: str = "newest"


app = FastAPI()


@app.post(path="/summarize_video")
def fetch_video_summary(video_urls: VideoUrls):
    with open(params_path, "r") as f:
        responses = yaml.safe_load(f).get("responses")

    try:
        summaries = main(
            channels=video_urls.channels,
            videos=video_urls.videos,
            LIMIT_TRANSCRIPT=video_urls.limit_transcript,
            sort_by=video_urls.sort_by,
        )

        data = {"summaries": summaries}
        status = responses.get("SUCCESS")
        status_code = statuses.SUCCESS.value

    except Exception as e:
        data = {"summaries": None}
        status = responses.get("ERROR")
        status = statuses.ERROR

    return JSONResponse(content={**data, **status}, status_code=status_code)
