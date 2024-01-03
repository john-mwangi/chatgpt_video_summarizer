from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

template = """system: You are a helpful assistant who provides helpful summaries 
to a video transcript. The format of the transcript is `timestamp - dialogue`.

{conversation_history}
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


if __name__ == "__main__":
    from dotenv import load_dotenv
    from langchain.chains import LLMChain
    from langchain.chat_models import ChatOpenAI

    from params import CHUNK_SIZE, transcript_dir

    load_dotenv()

    model = LLMChain(
        llm=ChatOpenAI(model="gpt-4-1106-preview"),
        prompt=prompt_template,
        memory=memory,
    )

    paths = transcript_dir.glob("*.txt")
    path = list(paths)[0]

    with open(path, mode="r") as f:
        transcript = [line.strip() for line in f.readlines()]

    transcripts = chunk_transcript(transcript, CHUNK_SIZE)

    for video_transcript in transcripts[:3]:
        question = f"""Consider the following video transcript: 
            
            {video_transcript} 
            
            Begin by providing a concise summary of the what is being discussed in 
            the transcript as a paragraph. Then follow it with bullet points of the 
            important points along with their associated timestamps."""

        msg = model.predict(question=question)

        print(msg, "\n\n")
