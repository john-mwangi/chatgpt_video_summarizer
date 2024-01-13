from pathlib import Path

import yaml
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).parent.parent.resolve()
transcript_dir = ROOT_DIR / "files/transcripts"
summaries_dir = ROOT_DIR / "files/summaries"
params_path = ROOT_DIR / "src/params.yaml"


class Params(BaseSettings):
    model: str
    CHUNK_SIZE: int
    SUMMARY_LIMIT: int
    BULLETS: int
    BATCH_CHUNKS: int
    LIMIT_TRANSCRIPT: None | float | int

    def load(path: Path = params_path):
        with open(path, mode="r") as f:
            params = yaml.safe_load(f)

        return Params(**params)


if __name__ == "__main__":
    print(Params.load().BATCH_CHUNKS)
    print(Params.load())
    print(dict(Params.load()))
