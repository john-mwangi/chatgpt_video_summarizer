"""Module for chatting with a video via a RAG"""

import os
import time

from langchain.text_splitter import TextSplitter
from pinecone import Pinecone, PodSpec

from video_summarizer.backend.src.utils import get_mongodb_client, logger


def get_create_pinecone_index(index_name: str):

    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

    available_idx = [i.get("name") for i in pc.list_indexes().get("indexes")]

    if index_name not in available_idx:
        pc.create_index(
            name=index_name,
            dimension=1536,  # https://www.pinecone.io/learn/openai-embeddings-v3/
            metric="cosine",
            spec=PodSpec(environment="gcp-starter"),
        )

        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    # get the created index
    index = pc.Index(index_name)
    logger.info(index.describe_index_stats())

    return index


def get_document(video_id: str):
    client, db = get_mongodb_client()
    db = client[db]
    transcripts = db.transcripts
    result = transcripts.find_one({"video_id": video_id})
    return result


def split_docs(res: dict):
    transcript = res.get("transcript")
    splitter = TextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = splitter.split_documents(transcript)
    return docs


if __name__ == "__main__":
    from dotenv import load_dotenv
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores.pinecone import Pinecone as PineconeLang

    load_dotenv()

    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")

    video_id = "JEBDfGqrAUA"
    vid = video_id.lower()

    # create an index
    index = get_create_pinecone_index(index_name=vid)

    # get embeddings
    embeddings = OpenAIEmbeddings()

    # insert docs to pinecone index
    res = get_document(video_id=video_id)
    docs = split_docs(res)

    vector_store = PineconeLang.from_documents(
        documents=docs, embedding=embeddings, index_name=vid
    )

    logger.info(vector_store)
