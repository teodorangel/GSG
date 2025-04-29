import pytest
from api.agent import run_plan
from api.models import PlanResponse

# Dummy components for patching
class DummyDBChain:
    @classmethod
    def from_llm(cls, llm, database, verbose=False):
        return cls()

    def run(self, query):
        # Return a mock spec string
        return "modelA:$100,modelB:$200"

class DummyDoc:
    def __init__(self, page_content):
        self.page_content = page_content

class DummyLLM:
    def generate(self, prompts):
        # Return an object with .generations attribute
        class Generation:
            def __init__(self, text):
                self.text = text
        return type("Answer", (), {"generations": [[Generation("step1\nstep2")]]})

@pytest.fixture(autouse=True)
def patch_agent(monkeypatch):
    import api.agent as agent

    # Patch SQLDatabaseChain
    monkeypatch.setattr(agent, "SQLDatabaseChain", DummyDBChain)
    # Patch Pinecone retriever
    dummy_retriever = type(
        "Rec",
        (),
        {"get_relevant_documents": lambda self, ids: [DummyDoc("doc1"), DummyDoc("doc2")]},
    )()
    monkeypatch.setattr(agent, "pinecone_retriever", dummy_retriever)
    # Patch LLM
    monkeypatch.setattr(agent, "llm", DummyLLM())
    yield


def test_run_plan_basic():
    # Call the planning function
    response = run_plan(product_ids=[1, 2], budget=500.0, site_size_sqft=1000)

    # Verify response structure
    assert isinstance(response, PlanResponse)
    # Steps should be split correctly
    assert response.steps == ["step1", "step2"]
    # bill_of_materials and estimates are placeholder empty dicts
    assert response.bill_of_materials == {}
    assert response.estimates == {}
