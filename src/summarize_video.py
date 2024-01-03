from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

template = """system: You are a helpful assistant who provides helpful responses 
to the video transcript below. The format of the transcript is `timestamp - dialogue`:

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

if __name__ == "__main__":
    from dotenv import load_dotenv
    from langchain.chains import LLMChain
    from langchain.chat_models import ChatOpenAI

    from params import transcript_dir

    LINES = 10

    load_dotenv()

    model = LLMChain(
        llm=ChatOpenAI(model="gpt-4-1106-preview"),
        prompt=prompt_template,
        memory=memory,
    )

    paths = transcript_dir.glob("*.txt")
    path = list(paths)[0]

    with open(path, mode="r") as f:
        lines = [line.strip() for line in f.readlines()]

    video_transcript = lines[:LINES]
    msg = model.predict(
        question=f"""Consider the following video transcript: {video_transcript} 
        Which is the first project and what timestamp mentions the project?""",
    )

    print(msg)
