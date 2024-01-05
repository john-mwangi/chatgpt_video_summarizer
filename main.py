from src.extract_transcript import main as extract_main
from src.summarize_video import main as summarise_main

if __name__ == "__main__":
    from pprint import pprint

    urls = [
        "https://www.youtube.com/watch?v=JEBDfGqrAUA",
        "https://www.youtube.com/watch?v=TRjq7t2Ms5I",
    ]
    for url in urls:
        extract_main(url=url)

    msgs = summarise_main()
    for msg in msgs:
        pprint(msg)
        print("\n\n")
