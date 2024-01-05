from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()
transcript_dir = ROOT_DIR / "transcripts"

CHUNK_SIZE = 10
LIMIT_CHUNKS = 4
SUMMARY_LIMIT = 150
BULLETS = 5
BATCH_CHUNKS = 2
