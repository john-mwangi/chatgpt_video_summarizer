from enum import Enum
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()

params_path = ROOT_DIR / f"video_summarizer/backend/configs/params.yaml"
video_keys = ["video_id", "video_url", "video_title"]


class statuses(Enum):
    SUCCESS = 200
    ERROR = 400
    NOT_FOUND = 404


class ModelParams(BaseSettings):
    MODEL: str
    CHUNK_SIZE: int
    SUMMARY_LIMIT: int
    BULLETS: int
    BATCH_CHUNKS: int

    def load(path: Path = params_path):
        with open(path, mode="r") as f:
            params = yaml.safe_load(f).get("model_params")

        return ModelParams(**params)


if __name__ == "__main__":
    print(ROOT_DIR)
    print(ModelParams.load().BATCH_CHUNKS)
    print(ModelParams.load())
    print(dict(ModelParams.load()))
