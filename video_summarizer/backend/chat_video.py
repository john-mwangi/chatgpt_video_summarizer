"""Module for chatting with a video via a RAG"""

import os
import time

import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, PodSpec
from pinecone.data.index import Index
from tqdm.auto import tqdm

from video_summarizer.backend.src.utils import get_mongodb_client, logger

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")

pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)


def get_create_pinecone_index(index_name: str):
    """Retrieve an index from Pinecode vectorstore"""

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
    logger.info(f"Pinecone index stats:\n {index.describe_index_stats()}")

    return index


def get_document(video_id: str):
    """Get a document related to a video from Mongodb"""

    client, db = get_mongodb_client()
    db = client[db]
    transcripts = db.transcripts
    result = transcripts.find_one({"video_id": video_id})
    return result


def upsert_documents_to_pinecone(
    idx: Index, video_id: str, index_name: str, delete=False
):
    """Inserts document to an index associated with a video id"""

    # delete the index
    if delete:
        pc.delete_index(index_name)
        vector_count = index.describe_index_stats().get("total_vector_count")
        assert vector_count == 0
        logger.info(f"Successfully deleted {index_name=}")

    # check that the index for this video is not empty
    stats = idx.describe_index_stats()
    total_vector_count = stats.get("total_vector_count")

    if total_vector_count > 0:
        logger.info(f"{index_name=} for is already populated")
        return None

    # convert transcript to dataframe
    res = get_document(video_id)
    transcript = res.get("transcript")

    df = pd.DataFrame(transcript)
    data = df[0].str.extract(r"\n(\d+:\d{2}:\d{2})\s-\s(.*)")
    data.columns = ["timestamp", "text"]

    # upload transcript to pinecone index
    batch_size = 100
    for i in tqdm(range(0, len(data), batch_size)):
        i_end = min(len(data), i + batch_size)
        batch = data.iloc[i:i_end]
        ids = [f"{video_id}-{i}" for i, x in batch.iterrows()]
        texts = [x["text"] for _, x in batch.iterrows()]
        embeds = embeddings.embed_documents(texts)
        metadata = [
            {"text": x["text"], "timestamp": x["timestamp"]}
            for _, x in batch.iterrows()
        ]
        index.upsert(vectors=zip(ids, embeds, metadata))
        logger.info(f"Successfully added content to {index_name=}")


if __name__ == "__main__":
    from langchain.embeddings.openai import OpenAIEmbeddings

    video_id = "JEBDfGqrAUA"
    index_name = video_id.lower()

    # create an index
    index = get_create_pinecone_index(index_name=index_name)

    # get embeddings
    embeddings = OpenAIEmbeddings()

    # insert content to vectorstore
    upsert_documents_to_pinecone(
        idx=index, video_id=video_id, delete=True, index_name=index_name
    )
