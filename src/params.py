from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()
transcript_dir = ROOT_DIR / "files/transcripts"
summaries_dir = ROOT_DIR / "files/summaries"

CHUNK_SIZE = 10
SUMMARY_LIMIT = 150
BULLETS = 5
BATCH_CHUNKS = 2

# Use one of the following values
# None to process entire video transcript
# (0-1) for a proportion of the transcript
# >=1 for a hardcorded number of transcript lines
LIMIT_TRANSCRIPT = 0.25
