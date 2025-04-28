import os
import json
import pytest
from unittest.mock import patch, MagicMock

from processors.ingest_worker import IngestWorker
from crawler.items import DataItem, ItemType

SAMPLE_ITEM = DataItem(
    url="https://example.com/page1",
    item_type=ItemType.PAGE,
    payload={
        "content": "<html><body><p>Hello world</p></body></html>"
    },
)

@pytest.fixture
def temp_jsonl(tmp_path):
    file = tmp_path / "out.jl"
    with open(file, 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            "url": SAMPLE_ITEM.url,
            "item_type": SAMPLE_ITEM.item_type.value,
            "payload": SAMPLE_ITEM.payload,
        }) + "\n")
    return str(file)

@patch("processors.ingest_worker.pinecone")
@patch("processors.ingest_worker.OpenAIEmbeddings")
@patch("processors.ingest_worker.HTMLLoader")
@patch("processors.ingest_worker.PyPDFLoader")

def test_ingest_file(mock_pdf_loader, mock_html_loader, mock_embeddings, mock_pinecone, temp_jsonl):
    # Setup mocks
    mock_index = MagicMock()
    mock_pinecone.Index.return_value = mock_index
    mock_embeddings.return_value.embed_documents.return_value = [[0.1, 0.2, 0.3]]

    # Fake loader returns document with page_content
    class FakeDoc:
        def __init__(self, content):
            self.page_content = content
    mock_loader_instance = MagicMock()
    mock_loader_instance.load.return_value = [FakeDoc("Hello world")]
    mock_html_loader.return_value = mock_loader_instance
    mock_pdf_loader.return_value = mock_loader_instance

    worker = IngestWorker(index_name="test-index", pinecone_api_key="key", pinecone_env="env")
    worker.ingest_file(temp_jsonl)

    # Verify upsert called
    assert mock_index.upsert.called
    args, kwargs = mock_index.upsert.call_args
    vectors = kwargs.get('vectors') or args[0]
    assert isinstance(vectors, list)
    assert vectors[0][0].startswith(SAMPLE_ITEM.url)

