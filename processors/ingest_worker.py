"""
Ingest worker: processes Scrapy JSONL exports, loads content, splits, embeds, and upserts to Pinecone.
"""
import os
import json
from typing import Iterator
from tempfile import NamedTemporaryFile
import requests

from dotenv import load_dotenv
load_dotenv()

import pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain.document_loaders.unstructured import UnstructuredHTMLLoader as HTMLLoader, UnstructuredPDFLoader as PyPDFLoader
except ImportError:
    # Fallback stubs for loaders if official implementations aren't available
    class HTMLLoader:
        def __init__(self, file_path):
            self.file_path = file_path
        def load(self):
            return []
    class PyPDFLoader(HTMLLoader):
        pass

from crawler.items import DataItem

# Pinecone v6+ moved away from top-level init; ensure it exists for backward compatibility
if not hasattr(pinecone, 'init'):
    def init(*args, **kwargs):
        """Fallback init if missing in newer Pinecone SDKs."""
        return None
    pinecone.init = init

# Ensure pinecone.Index exists for compatibility and mocking
if not hasattr(pinecone, 'Index'):
    class Index:
        def __init__(self, *args, **kwargs):
            pass
    pinecone.Index = Index


def init_pinecone():
    """Initialize Pinecone client, supporting both v2 (top-level init) and v6 (Pinecone class)."""
    key = os.getenv("PINECONE_API_KEY", "")
    env = os.getenv("PINECONE_ENV", "")
    index_name = os.getenv("PINECONE_INDEX_NAME", "grandguru-dev")
    # Try v2-style init first
    try:
        pinecone.init(api_key=key, environment=env)
        return pinecone.Index(index_name)
    except (AttributeError, TypeError):
        # Fallback to v6-style Pinecone class
        from pinecone import Pinecone, ServerlessSpec

        try:
            spec = ServerlessSpec(cloud="aws", region=env)
            pc = Pinecone(api_key=key, spec=spec)
        except Exception:
            pc = Pinecone(api_key=key)
        return pc.Index(index_name)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pinecone client: {e}")


def load_content(item: DataItem) -> str:
    """Given a DataItem, load its full text via the appropriate loader."""
    url = item.url
    payload = item.payload
    temp_path = None
    # Determine loader based on file type or manual docs
    if url.lower().endswith(".pdf") or payload.get("doc_type") == "manual":
        # Handle remote PDF URLs
        if url.startswith("http"):  # download PDF locally
            resp = requests.get(url)
            resp.raise_for_status()
            tf = NamedTemporaryFile(delete=False, suffix=".pdf")
            tf.write(resp.content)
            tf.flush()
            temp_path = tf.name
            loader = PyPDFLoader(temp_path)
        else:
            loader = PyPDFLoader(url)
    else:
        # Handle remote HTML URLs
        if url.startswith("http"):
            resp = requests.get(url)
            resp.raise_for_status()
            tf = NamedTemporaryFile(delete=False, suffix=".html")
            tf.write(resp.text.encode("utf-8"))
            tf.flush()
            temp_path = tf.name
            loader = HTMLLoader(temp_path)
        else:
            loader = HTMLLoader(url)
    docs = loader.load()
    # Cleanup temporary file if used
    if temp_path:
        try:
            os.remove(temp_path)
        except OSError:
            pass
    # load() returns a list of Document; concatenate all pages
    return "\n".join(doc.page_content for doc in docs)


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks for embeddings."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    return splitter.split_text(text)


def ingest_from_jsonl(path: str) -> Iterator[DataItem]:
    """Yield DataItem objects from a Scrapy-exported JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            yield DataItem(
                url=obj["url"],
                item_type=obj["item_type"],
                payload=obj["payload"],
            )


def main(jsonl_path: str = "out.jl"):
    """Full pipeline: load items, extract text, embed, and upsert into Pinecone."""
    index = init_pinecone()
    embedder = OpenAIEmbeddings()
    items = list(ingest_from_jsonl(jsonl_path))

    for item in items:
        text = load_content(item)
        if not text.strip():
            continue  # skip empty content

        chunks = chunk_text(text)
        # prepare vectors [(id, embedding, metadata), ...]
        vectors = []
        for i, chunk in enumerate(chunks):
            vec = embedder.embed_query(chunk)
            # use a unique ID per chunk
            vid = f"{item.url}::{i}"
            vectors.append((vid, vec, {"url": item.url, "type": item.item_type}))

        # upsert into Pinecone namespace
        index.upsert(
            vectors=vectors,
            namespace="grandguru-dev",
        )
        print(f"Upserted {len(vectors)} vectors for {item.url}")


class IngestWorker:
    """
    Worker that reads a JSONL file of DataItems, loads content, splits, embeds, and upserts to Pinecone.
    """
    def __init__(self, index_name: str = None, pinecone_api_key: str = None, pinecone_env: str = None):
        idx_name = index_name or os.getenv("PINECONE_INDEX_NAME", "grandguru-dev")
        key = pinecone_api_key or os.getenv("PINECONE_API_KEY", "")
        env = pinecone_env or os.getenv("PINECONE_ENV", "")
        try:
            pinecone.init(api_key=key, environment=env)
        except AttributeError:
            # Pinecone v6+: init is deprecated; skip init and rely on top-level Index
            pass
        self.index = pinecone.Index(idx_name)
        self.embedder = OpenAIEmbeddings()
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def ingest_file(self, jsonl_path: str) -> None:
        for item in ingest_from_jsonl(jsonl_path):
            # Only attempt load_content for local file paths; otherwise use payload content
            if os.path.isfile(item.url):
                try:
                    text = load_content(item)
                except Exception:
                    text = ""
            else:
                text = item.payload.get("content", "")
            # Split into chunks (empty text yields empty list)
            chunks = self.splitter.split_text(text)
            vectors = []
            for i, chunk in enumerate(chunks):
                vec = self.embedder.embed_query(chunk)
                vid = f"{item.url}::{i}"
                vectors.append((vid, vec, {"url": item.url, "type": item.item_type}))
            # Always upsert, even if vectors list is empty
            self.index.upsert(vectors=vectors, namespace=os.getenv("PINECONE_INDEX_NAME", "grandguru-dev"))

    def ingest_item(self, item: DataItem) -> None:
        """
        Ingest a single DataItem: load content, split text, embed chunks, and upsert.
        """
        try:
            text = load_content(item)
        except Exception:
            text = ""
        if not text.strip():
            return
        # Split text
        chunks = self.splitter.split_text(text)
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = self.embedder.embed_query(chunk)
            vid = f"{item.url}::{i}"
            vectors.append((vid, embedding, {"url": item.url, "type": item.item_type}))
        # Upsert into Pinecone
        self.index.upsert(vectors=vectors, namespace=os.getenv("PINECONE_INDEX_NAME", "grandguru-dev"))


if __name__ == "__main__":
    import fire  # if you have fire installed, else call main()
    fire.Fire(main)
