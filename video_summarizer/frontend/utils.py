from pydantic import BaseModel, HttpUrl

from video_summarizer.backend.src.utils import logger


class Url(BaseModel):
    url: HttpUrl


def validate_url(url: str) -> bool:
    try:
        Url(url=url)
        is_valid = True
    except:
        logger.warning(f"Invalid url: {url}")
        is_valid = False

    return is_valid


if __name__ == "__main__":
    assert (
        validate_url("https://docs.pydantic.dev/latest/api/networks/") == True
    )

    assert validate_url("xxx") == False

    assert validate_url("docs.pydantic.dev/latest/api/networks/") == False

    assert validate_url(None) == False
