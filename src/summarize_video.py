from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

template = """system: You are a helpful assistant who provides helpful summaries 
to a video transcript. The format of the video transcript is `timestamp - dialogue`.

user: {question}
assistant:
"""

prompt_template = PromptTemplate(
    input_variables=["conversation_history", "question", "video_transcript"],
    template=template,
)

memory = ConversationBufferMemory(
    memory_key="conversation_history", ai_prefix="assistant", human_prefix="user"
)


def chunk_transcript(transcript: list[str], chunk_size: int) -> list[list[str]]:
    """Converts a transcript into a smaller chunks"""

    result = []
    sublist = []

    for _, t in enumerate(transcript):
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


if __name__ == "__main__":
    import pickle

    from dotenv import load_dotenv
    from langchain.chains import LLMChain
    from langchain.chat_models import ChatOpenAI

    from params import (
        BATCH_CHUNKS,
        BULLETS,
        CHUNK_SIZE,
        LIMIT_CHUNKS,
        SUMMARY_LIMIT,
        transcript_dir,
    )

    load_dotenv()

    model = LLMChain(
        llm=ChatOpenAI(model="gpt-4-1106-preview"),
        prompt=prompt_template,
    )

    paths = transcript_dir.glob("*.txt")
    path = list(paths)[0]

    with open(path, mode="r") as f:
        transcript = [line.strip() for line in f.readlines()]

    transcripts = chunk_transcript(transcript, CHUNK_SIZE)

    # summaries = []

    # for video_transcript in transcripts[:LIMIT_CHUNKS]:
    #     summary = create_summary(
    #         model=model,
    #         limit=SUMMARY_LIMIT,
    #         video_transcript=video_transcript,
    #         bullets=BULLETS,
    #     )
    #     summaries.append(summary)

    # with open("summaries.pkl", mode="wb") as f:
    #     pickle.dump(summaries, f)

    with open("summaries.pkl", mode="rb") as f:
        summaries = pickle.load(f)

    breakpoint()
    batch_summaries = chunk_transcript(transcript=summaries, chunk_size=BATCH_CHUNKS)
