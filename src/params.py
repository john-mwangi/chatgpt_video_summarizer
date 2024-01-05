from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()
transcript_dir = ROOT_DIR / "files/transcripts"
summaries_dir = ROOT_DIR / "files/summaries"

CHUNK_SIZE = 10
LIMIT_TRANSCRIPT = 4  # use None to process entire video transcript
SUMMARY_LIMIT = 150
BULLETS = 5
BATCH_CHUNKS = 2
