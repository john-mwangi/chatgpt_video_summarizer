import json
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tqdm import tqdm

from . import params


def init_model():
    """Initialise an LLM"""

    template = """system: You are a helpful assistant who provides helpful summaries 
    to a video transcript. The format of the video transcript is `timestamp - dialogue`.

    user: {question}
    assistant:
    """

    prompt_template = PromptTemplate(
        input_variables=["conversation_history", "question", "video_transcript"],
        template=template,
    )

    model = LLMChain(
        llm=ChatOpenAI(model="gpt-4-1106-preview"),
        prompt=prompt_template,
    )

    return model


def chunk_a_list(data: list[str], chunk_size: int) -> list[list[str]]:
    """Converts a long list to a smaller one by combining its items"""

    result = []
    sublist = []

    for _, t in enumerate(data):
        if t.strip():
            sublist.append(t)
        if len(sublist) == chunk_size:
            result.append(sublist)
            sublist = []
    if sublist:
        result.append(sublist)

    return result


def create_summary(model, limit, video_transcript, bullets) -> str:
    """Provides a summary for a video transcript"""

    question = f"""Consider the following video transcript: 
    
    {video_transcript} 
    
    Begin by providing a concise single sentence summary of the what 
    is being discussed in the transcript. Then follow it with bullet 
    points of the {bullets} most important points along with their associated 
    timestamps. The total number of words should not be more than {limit}.
    """

    summary = model.predict(question=question)
    return summary


def check_if_summarised(t_path: Path, summary_dir: Path):
    """Checks if a transcript has already been summarised"""

    t_name = t_path.stem

    s_paths = list(summary_dir.glob("*.json"))
    summary_names = [s.stem for s in s_paths]

    is_summarised = any([t_name == s_name for s_name in summary_names])

    with open(f"{summary_dir / t_name}.json") as f:
        summary = json.load(f).get("summary")

    return is_summarised, summary


def main():
    load_dotenv()

    model = init_model()

    paths = list(params.transcript_dir.glob("*.txt"))
    video_ids = [p.stem.split("vid:")[-1] for p in paths]
    files = list(zip(video_ids, paths))

    for i, file in enumerate(files):
        vid, path = file

        is_summarised, content = check_if_summarised(
            t_path=path, summary_dir=params.summaries_dir
        )

        if is_summarised:
            print(f"Video '{path.stem}' has already been summarised\n\n")
            pprint(content)
            exit()

        print(f"Summarising video '{path.stem}' ...")

        with open(path, mode="r") as f:
            transcript = [line.strip() for line in f.readlines()]

        transcripts = chunk_a_list(transcript, params.CHUNK_SIZE)

        if params.LIMIT_TRANSCRIPT is not None:
            transcripts = transcripts[: params.LIMIT_TRANSCRIPT]

        # recursively chunk the list & summarise until len(summaries) == 1
        summaries = []
        while len(summaries) != 1:
            for video_transcript in tqdm(transcripts):
                summary = create_summary(
                    model=model,
                    limit=params.SUMMARY_LIMIT,
                    video_transcript=video_transcript,
                    bullets=params.BULLETS,
                )
                summaries.append(summary)

            summaries = chunk_a_list(summaries, params.CHUNK_SIZE)

        assert len(summaries) == 1, "You have not created a summary of summaries"

        msg = create_summary(
            model=model,
            limit=params.SUMMARY_LIMIT,
            video_transcript=summaries[0],
            bullets=params.BULLETS,
        )

        video_summary = {"video_id": vid, "summary": msg}

        if not params.summaries_dir.exists():
            params.summaries_dir.mkdir()

        file_path = params.summaries_dir / f"{paths[i].stem}.json"

        with open(file_path, mode="w") as f:
            json.dump(video_summary, f)

    return msg


if __name__ == "__main__":
    msg = main()
    pprint(msg)
