from typing import List, Optional
import os

# Attempt to import ai_function from pydantic_ai, else use a no-op decorator
try:
    from pydantic_ai import ai_function
except ImportError:
    def ai_function(fn):
        return fn

from api.models import QAResponse, PlanResponse

# LangChain imports
# Import OpenAI LLM class, preferring community provider, fallback to langchain-openai
try:
    from langchain_community.llms import OpenAI
except ImportError:
    from langchain_openai import OpenAI
# SQLDatabaseChain import (with fallback)
try:
    from langchain_community.chains import SQLDatabaseChain
except ImportError:
    # Fallback stub for SQLDatabaseChain
    class SQLDatabaseChain:
        @classmethod
        def from_llm(cls, llm, database, verbose=False):
            return cls()
        def run(self, query: str) -> str:
            raise NotImplementedError("SQLDatabaseChain is not available but was called")
# RetrievalQA import (with fallback)
try:
    from langchain_community.chains import RetrievalQA
except ImportError:
    # Fallback stub for RetrievalQA
    class RetrievalQA:
        def __init__(self, llm, retriever):
            pass
        def run(self, query: str) -> str:
            raise NotImplementedError("RetrievalQA is not available but was called")
from langchain.embeddings import OpenAIEmbeddings
# Pinecone retriever import is deferred to runtime within AI functions to avoid import-time errors
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Initialize LLM
llm = OpenAI()

# Setup Database engine lazily from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
_engine = None

def get_engine():
    """Lazily initialize and return the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        _engine = create_engine(DATABASE_URL)
    return _engine

# Setup Pinecone retriever (wrapped to avoid import-time errors if Pinecone client missing or misconfigured)
pinecone_retriever = None  # Will be configured at runtime or overridden in tests


@ai_function
def run_qa(query: str, product_id: Optional[int] = None) -> QAResponse:
    """
    Perform RetrievalQA combining structured facts from Postgres and docs from Pinecone.

    Args:
        query (str): The question to ask.
        product_id (Optional[int]): Optional product context.

    Returns:
        QAResponse: The answer and list of source references.
    """
    # SQL database chain for structured data
    db_chain = SQLDatabaseChain.from_llm(llm=llm, database=get_engine(), verbose=False)
    # Retrieval QA for unstructured docs
    retriever_chain = RetrievalQA(llm=llm, retriever=pinecone_retriever)

    # Query both sources
    structured = db_chain.run(
        f"{query} for product_id {product_id}" if product_id else query
    )
    unstructured = retriever_chain.run(query)

    # Combine results
    answer = f"{structured}\n{unstructured}"
    sources: List[str] = []  # TODO: collect actual source IDs or URLs
    return QAResponse(answer=answer, sources=sources)


@ai_function
def run_plan(product_ids: List[int], budget: Optional[float] = None, site_size_sqft: Optional[int] = None) -> PlanResponse:
    """
    Generate a step-by-step deployment plan, BOM, and cost estimates.

    Args:
        product_ids (List[int]): List of selected product IDs.
        budget (Optional[float]): Budget constraint.
        site_size_sqft (Optional[int]): Site area in sqft.

    Returns:
        PlanResponse: Steps, bill of materials, and estimates.
    """
    # Retrieve product specs and prices
    db_chain = SQLDatabaseChain.from_llm(llm=llm, database=get_engine(), verbose=False)
    specs = db_chain.run(
        f"SELECT model, price FROM products WHERE id IN ({','.join(map(str, product_ids))})"
    )

    # Fetch relevant documentation snippets if retriever is configured
    docs = pinecone_retriever.get_relevant_documents(str(product_ids)) if pinecone_retriever else []

    # Generate plan via LLM prompt
    prompt = (
        f"Create a deployment plan with steps, BOM, and cost estimates for products {product_ids}"  \
        f" under a budget of {budget} and site size {site_size_sqft} sqft.\n"  \
        f"Product specs: {specs}\nDocumentation: {[d.page_content for d in docs]}"
    )
    gen = llm.generate([prompt])
    plan_text = gen.generations[0][0].text

    # Parse outputs (simple newline split)
    steps = [line for line in plan_text.split("\n") if line]
    bill_of_materials = {}  # TODO: parse BOM details from plan_text
    estimates = {}         # TODO: parse estimates from plan_text

    return PlanResponse(steps=steps, bill_of_materials=bill_of_materials, estimates=estimates) 