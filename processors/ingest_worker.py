"""
Ingest worker: processes Scrapy JSONL exports, loads content, splits, embeds, and upserts to Pinecone.
"""
import json
import os
import tempfile

import pinecone
from crawler.items import DataItem, ItemType
from langchain_community.document_loaders import UnstructuredHTMLLoader as HTMLLoader
from langchain_community.document_loaders import UnstructuredPDFLoader as PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter


class IngestWorker:
    """
    Worker that reads a JSONL file of DataItems, loads documents via LangChain loaders,
    splits into chunks, embeds, and upserts vectors into Pinecone.
    """

    def __init__(self, index_name: str, pinecone_api_key: str = None, pinecone_env: str = None):
        # Initialize Pinecone client
        if pinecone_api_key or pinecone_env:
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)  # Reason: connect to Pinecone
        self.index = pinecone.Index(index_name)
        self.embeddings = OpenAIEmbeddings()
        self.splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def ingest_file(self, filepath: str) -> None:
        """
        Read JSON lines from filepath and ingest into Pinecone index.

        Args:
            filepath: Path to the JSONL file exported by Scrapy.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                item = DataItem(
                    url=data['url'],
                    item_type=ItemType(data['item_type']),
                    payload=data['payload'],
                )
                # Load documents via appropriate loader
                if 'file_path' in item.payload and item.payload['file_path'].lower().endswith('.pdf'):
                    loader = PyPDFLoader(item.payload['file_path'])
                    docs = loader.load()
                else:
                    html = item.payload.get('content', '')
                    # Write HTML to a temp file for loader
                    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as tf:
                        tf.write(html)
                        tmp_path = tf.name
                    loader = HTMLLoader(tmp_path)
                    docs = loader.load()
                    os.remove(tmp_path)

                # Ensure metadata on docs for text splitter compatibility
                for doc in docs:
                    if not hasattr(doc, 'metadata'):
                        doc.metadata = {}

                # Split into chunks
                chunks = self.splitter.split_documents(docs)
                texts = [doc.page_content for doc in chunks]

                # Create embeddings
                vectors = []
                embeddings = self.embeddings.embed_documents(texts)
                for idx, emb in enumerate(embeddings):
                    vid = f"{item.url}-{idx}"
                    vectors.append((vid, emb, {'url': item.url, 'chunk': idx}))

                # Upsert to Pinecone
                self.index.upsert(vectors=vectors)
