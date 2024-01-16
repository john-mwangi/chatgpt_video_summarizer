from pprint import pprint

import yaml
from scrapetube import get_channel

from src.configs import video_urls_path
from src.extract_transcript import main as extract_main
from src.summarize_video import main as summarise_main


def get_videos_from_channel(channel_url: str, sort_by: str, top_n: int) -> list[str]:
    """Returns a list of video urls from a YouTube channel"""

    videos = get_channel(channel_url=channel_url, sort_by=sort_by)

    vids = []
    counter = 0

    for video in videos:
        vids.append(video["videoId"])
        counter += 1
        if counter == top_n:
            break

    return [f"https://www.youtube.com/watch?v={v}" for v in vids]


def load_urls(video_urls: dict, sort_by: str) -> list[str]:
    """Loads videos defined in a config file

    Args:
    ---
    top_n: maximum number of videos to load from a channel
    sort_by: sort videos by

    Returns:
    ---
    list of YouTube video urls
    """

    top_n = video_urls.get("top_n")
    channels = video_urls.get("channels")

    if channels is not None:
        for channel in channels:
            urls = get_videos_from_channel(
                channel_url=channel, top_n=top_n, sort_by=sort_by
            )

    v_urls = video_urls.get("videos")

    if (channels is None) | (len(channels) == 0) and v_urls is not None:
        return v_urls
    elif (v_urls is None) | (len(v_urls) == 0) and channels is not None:
        return urls
    elif (channels is None) | (len(channels) == 0) and (v_urls is None) | (
        len(v_urls) == 0
    ):
        raise ValueError("Update video_urls.yaml")
    else:
        urls.extend(v_urls)
        return set(urls)


def main(
    channels: list = None,
    videos: list = None,
    LIMIT_TRANSCRIPT: int | float | None = 0.25,
    top_n: int = 2,
    sort_by: str = "newest",
):
    """
    Use one of the following values for `LIMIT_TRANSCRIPT_`
    None to process entire video transcript
    (0-1) for a proportion of the transcript
    >=1 for a hardcorded number of transcript lines
    """

    video_urls = {}
    video_urls["channels"] = channels
    video_urls["videos"] = videos
    video_urls["top_n"] = top_n

    yt_urls = load_urls(video_urls, sort_by=sort_by)

    print("Sorting YouTube videos by:", sort_by)
    print("Videos to summarise:", yt_urls)

    for url in yt_urls:
        extract_main(url=url)

    msgs = summarise_main(LIMIT_TRANSCRIPT)
    return msgs


if __name__ == "__main__":
    channels = [
        "https://www.youtube.com/@ArjanCodes",
        "https://www.youtube.com/@CBSNews",
    ]
    videos = [
        "https://www.youtube.com/watch?v=JEBDfGqrAUA",
        "https://www.youtube.com/watch?v=TRjq7t2Ms5I",
    ]

    msgs = main(channels, videos)
    for msg in msgs:
        pprint(msg)
        print("\n\n")
