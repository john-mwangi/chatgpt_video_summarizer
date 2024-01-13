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


def load_urls(video_urls: dict, sort_by: str = "newest") -> list[str]:
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

    if channels is None and v_urls is not None:
        return v_urls
    elif v_urls is None and channels is not None:
        return urls
    elif channels is None and v_urls is None:
        raise ValueError("Update video_urls.yaml")
    else:
        urls.extend(v_urls)
        return set(urls)


def main():
    with open(video_urls_path, "r") as f:
        video_urls = yaml.safe_load(f)

    yt_urls = load_urls(video_urls)

    print("YouTube video urls to summarise:", yt_urls)

    for url in yt_urls:
        extract_main(url=url)

    msgs = summarise_main()
    return msgs


if __name__ == "__main__":
    msgs = main()
    for msg in msgs:
        pprint(msg)
        print("\n\n")
