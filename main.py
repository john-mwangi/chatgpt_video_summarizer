from src.extract_transcript import main as extract_main
from src.summarize_video import main as summarise_main

if __name__ == "__main__":
    from pprint import pprint

    url = "https://www.youtube.com/watch?v=JEBDfGqrAUA"
    extract_main(url=url)
    summary = summarise_main()
    pprint(summary)
