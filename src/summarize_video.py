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


if __name__ == "__main__":
    import pickle

    from dotenv import load_dotenv
    from langchain.chains import LLMChain
    from langchain.chat_models import ChatOpenAI

    import params

    load_dotenv()

    model = LLMChain(
        llm=ChatOpenAI(model="gpt-4-1106-preview"),
        prompt=prompt_template,
    )

    paths = params.transcript_dir.glob("*.txt")
    path = list(paths)[0]

    with open(path, mode="r") as f:
        transcript = [line.strip() for line in f.readlines()]

    transcripts = chunk_a_list(transcript, params.CHUNK_SIZE)

    # recursively chunk the list & summarise until len(summaries) == 1
    summaries = []
    while len(summaries) != 1:
        for video_transcript in transcripts[: params.LIMIT_CHUNKS]:  # TODO: allow None
            summary = create_summary(
                model=model,
                limit=params.SUMMARY_LIMIT,
                video_transcript=video_transcript,
                bullets=params.BULLETS,
            )
            summaries.append(summary)

        summaries = chunk_a_list(summaries, params.CHUNK_SIZE)

    with open("summaries.pkl", mode="wb") as f:
        pickle.dump(summaries, f)

    breakpoint()
