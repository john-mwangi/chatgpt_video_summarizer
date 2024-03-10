"""Module for chatting with a video via a RAG"""

import os
import time
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone as PineconeVectorStore
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
    idx: Index, video_id: str, index_name: str, embeddings: OpenAIEmbeddings
):
    """Inserts document to an index associated with a video id"""

    # check that the index for this video is not empty
    stats = idx.describe_index_stats()
    total_vector_count = stats.get("total_vector_count")

    if total_vector_count > 0:
        logger.info(f"{index_name=} for is already populated")
        return

    # convert transcript to dataframe
    res = get_document(video_id)
    transcript = res.get("transcript")

    df = pd.DataFrame(transcript)
    if df.isnull().values.any():
        logger.error("df contains null values")
        return

    data = df[0].str.extract(r"\n(\d+:\d{2}:\d{2})\s-\s(.*)")
    data.columns = ["timestamp", "text"]

    # upload transcript to pinecone index
    batch_size = 100
    for i in tqdm(range(0, len(data), batch_size)):
        i_end = min(len(data), i + batch_size)
        batch = data.iloc[i:i_end]

        texts = [str(x["text"]) for _, x in batch.iterrows()]
        ids = [f"{uuid4().hex}" for _ in range(len(texts))]

        embeds = embeddings.embed_documents(texts)

        metadata = [
            {"text": str(x["text"]), "timestamp": str(x["timestamp"])}
            for _, x in batch.iterrows()
        ]

        idx.upsert(vectors=zip(ids, embeds, metadata))

    logger.info(f"Successfully added content to {index_name=}")


def main(video_id: str, delete_index=False, embeddings=OpenAIEmbeddings()):

    index_name = video_id.lower()

    # delete the index
    if delete_index:
        try:
            pc.delete_index(index_name)
            logger.info(f"Successfully deleted {index_name=}")
        except:
            logger.info(f"{index_name=} already deleted")

    # create an index
    index = get_create_pinecone_index(index_name=index_name)

    # insert content to vectorstore
    upsert_documents_to_pinecone(
        idx=index,
        video_id=video_id,
        index_name=index_name,
        embeddings=embeddings,
    )

    # use RAG ("text" is from the metadata)
    vectorstore = PineconeVectorStore(
        index=index, embedding=embeddings, text_key="text"
    )

    query = "What is vector search?"
    query_res = vectorstore.similarity_search({"query": query, "k": 3})
    # query_res = vectorstore.similarity_search(query=query)
    logger.info(query_res)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()

    # VIDEO_ID = "JEBDfGqrAUA"
    parser.add_argument(
        "--video_id", help="The video id to chat with", required=True
    )
    parser.add_argument(
        "--delete_index",
        help="Delete the Pinecone index",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    logger.info(args)

    main(video_id=args.video_id, delete_index=args.delete_index)
