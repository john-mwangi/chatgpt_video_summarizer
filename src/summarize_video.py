import json
from pathlib import Path

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

    is_summarised = False
    summary = None

    t_name = t_path.stem

    s_paths = list(summary_dir.glob("*.json"))
    summary_names = [s.stem for s in s_paths]

    is_summarised = any([t_name == s_name for s_name in summary_names])

    if is_summarised:
        with open(f"{summary_dir / t_name}.json") as f:
            summary = json.load(f).get("summary")

    return is_summarised, summary


# Define a function to use create_summary to summarize a single transcript
def summarize_transcript_with_model(transcript, bullets, model, limit):
    summary = create_summary(model, limit, transcript, bullets)
    return summary


# Define a function to combine summaries in chunks and summarize those chunks using the external model
def summarize_chunked_summaries_with_model(
    summaries, chunk_size, bullets, model, limit
):
    # list of lists / list of transcript summaries
    chunked_summaries = [
        summaries[i : i + chunk_size] for i in range(0, len(summaries), chunk_size)
    ]

    # join list contents into a single prompt/string and send to model
    combined_summaries = [
        summarize_transcript_with_model(" ".join(chunk), bullets, model, limit)
        for chunk in tqdm(chunked_summaries)
    ]

    # join together and send to model
    return summarize_transcript_with_model(
        " ".join(combined_summaries), bullets, model, limit
    )


# Function to summarize a list of transcripts using the external model
def summarize_list_of_transcripts_with_model(transcripts, bullets, model, limit):
    summaries = [
        summarize_transcript_with_model(transcript, bullets, model, limit)
        for transcript in tqdm(transcripts)
    ]
    return summaries


def main():
    load_dotenv()

    model = init_model()
    msgs = []

    paths = list(params.transcript_dir.glob("*.txt"))
    video_ids = [p.stem.split("vid:")[-1] for p in paths]
    files = list(zip(video_ids, paths))

    for i, file in enumerate(files):
        vid, path = file

        is_summarised, msg = check_if_summarised(
            t_path=path, summary_dir=params.summaries_dir
        )

        if is_summarised:
            print(f"Video '{path.stem}' has already been summarised")
            msgs.append(msg)

        else:
            print(f"Summarising video '{path.stem}' ...")

            with open(path, mode="r") as f:
                transcript = [line.strip() for line in f.readlines()]

            # Chunk the entire transcript into list of lines
            transcripts = chunk_a_list(transcript, params.CHUNK_SIZE)

            if (params.LIMIT_TRANSCRIPT is not None) & (params.LIMIT_TRANSCRIPT >= 1):
                transcripts = transcripts[: params.LIMIT_TRANSCRIPT]

            elif params.LIMIT_TRANSCRIPT < 1:
                length = len(transcripts) * params.LIMIT_TRANSCRIPT
                transcripts = transcripts[: int(length)]

            else:
                raise ValueError("incorrect value for LIMIT_TRANSCRIPT")

            # Summary of summaries: recursively chunk the list & summarise until len(summaries) == 1
            # Summarize each transcript using the external model
            list_of_summaries = summarize_list_of_transcripts_with_model(
                transcripts, params.BULLETS, model, params.SUMMARY_LIMIT
            )

            # Combine summaries in chunks and summarize them iteratively until a single summary is obtained
            while len(list_of_summaries) > 1:
                list_of_summaries = [
                    summarize_chunked_summaries_with_model(
                        list_of_summaries,
                        params.CHUNK_SIZE,
                        params.BULLETS,
                        model,
                        params.SUMMARY_LIMIT,
                    )
                ]

            # Output the final summary
            assert len(list_of_summaries) == 1, "Not a summary of summaries"
            msg = list_of_summaries[0]

            video_summary = {"video_id": vid, "summary": msg}

            if not params.summaries_dir.exists():
                params.summaries_dir.mkdir()

            file_path = params.summaries_dir / f"{paths[i].stem}.json"

            with open(file_path, mode="w") as f:
                json.dump(video_summary, f)

            msgs.append(msg)
    return msgs
