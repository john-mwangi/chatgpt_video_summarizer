import pickle

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tqdm import tqdm

import params


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


def main():
    load_dotenv()

    model = init_model()

    paths = params.transcript_dir.glob("*.txt")
    path = list(paths)[0]

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

    if not params.summaries_path.parent.exists():
        params.summaries_path.parent.mkdir()

    with open(params.summaries_path, mode="wb") as f:
        pickle.dump(msg, f)

    return msg


if __name__ == "__main__":
    from pprint import pprint

    msg = main()
    pprint(msg)
