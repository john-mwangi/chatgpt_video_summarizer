import yaml
from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse
from main import main
from pydantic import BaseModel

from video_summarizer.configs.configs import params_path, statuses


class VideoUrls(BaseModel):
    channels: list[str] = []
    videos: list[str] = []
    limit_transcript: float | int | None = 0.25
    top_n: int = 2
    sort_by: str = "newest"


app = FastAPI()
router_v1 = APIRouter()


@router_v1.post(path="/summarize_video")
def fetch_video_summary(video_urls: VideoUrls):
    """Summarize a video using AI:

    Args:
    ---
    * channels: a list of channels to retrive a video(s) to summarise from based on `sort_by` and `top_n` parameters\n
    * video: a list of video urls to summarise\n
    * limit_transcript: portion of the video transcript to summarise
    (None=full, <1 = partial, >=1 = number of chuncks)\n
    * top_n: retrieves this number of video from a channel to summarise\n
    * sort_by: sorts `top_n`

    Returns:
    ---
    A list of video summaries
    """

    with open(params_path, "r") as f:
        responses = yaml.safe_load(f).get("responses")

    try:
        summaries = main(
            channels=video_urls.channels,
            videos=video_urls.videos,
            LIMIT_TRANSCRIPT=video_urls.limit_transcript,
            sort_by=video_urls.sort_by,
        )

        data = {"data": {"summaries": summaries}}
        status = responses.get("SUCCESS")
        status_code = statuses.SUCCESS.value

    except Exception as e:
        data = {"summaries": None}
        status = responses.get("ERROR")
        status_code = statuses.ERROR.value

    return JSONResponse(content={**data, **status}, status_code=status_code)


# Mount the router on the app
app.include_router(router_v1, prefix="/api/v1")
