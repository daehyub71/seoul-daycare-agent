"""
LangGraph Workflow Builder
Defines the 4-stage workflow: Analyzer → Retriever → Generator → Post Processor
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, END

sys.path.insert(0, str(Path(__file__).parent.parent))
from workflows.nodes import (
    query_analyzer_node,
    document_retriever_node,
    answer_generator_node,
    post_processor_node,
)


class WorkflowState(TypedDict):
    """Complete workflow state structure"""

    # Input
    query: str

    # Query Analyzer outputs
    search_intent: str
    filters: dict
    keywords: list

    # Document Retriever outputs
    search_results: list

    # Answer Generator outputs
    answer: str

    # Post Processor outputs
    metadata: dict


def build_search_workflow():
    """
    Build the LangGraph workflow

    Workflow stages:
    1. Query Analyzer: Extract intent, filters, and keywords
    2. Document Retriever: Hybrid search (vector + database filter)
    3. Answer Generator: Generate natural language answer
    4. Post Processor: Validate and enhance the answer

    Returns:
        Compiled LangGraph workflow
    """
    # Create workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("document_retriever", document_retriever_node)
    workflow.add_node("answer_generator", answer_generator_node)
    workflow.add_node("post_processor", post_processor_node)

    # Define edges (linear flow)
    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", "document_retriever")
    workflow.add_edge("document_retriever", "answer_generator")
    workflow.add_edge("answer_generator", "post_processor")
    workflow.add_edge("post_processor", END)

    # Compile workflow
    app = workflow.compile()

    return app


# Global workflow instance
_workflow_app = None


def get_workflow():
    """Get or create global workflow instance"""
    global _workflow_app
    if _workflow_app is None:
        _workflow_app = build_search_workflow()
    return _workflow_app


async def run_search_workflow(query: str) -> dict:
    """
    Run the complete search workflow

    Args:
        query: User search query

    Returns:
        Final workflow state with answer and metadata
    """
    workflow = get_workflow()

    # Initialize state
    initial_state = {
        "query": query,
        "search_intent": "",
        "filters": {},
        "keywords": [],
        "search_results": [],
        "answer": "",
        "metadata": {},
    }

    # Run workflow
    final_state = await workflow.ainvoke(initial_state)

    return final_state


def run_search_workflow_sync(query: str) -> dict:
    """
    Synchronous version of run_search_workflow

    Args:
        query: User search query

    Returns:
        Final workflow state with answer and metadata
    """
    workflow = get_workflow()

    # Initialize state
    initial_state = {
        "query": query,
        "search_intent": "",
        "filters": {},
        "keywords": [],
        "search_results": [],
        "answer": "",
        "metadata": {},
    }

    # Run workflow
    final_state = workflow.invoke(initial_state)

    return final_state


if __name__ == "__main__":
    # Test workflow
    print("=" * 60)
    print("Testing Seoul Daycare Search Workflow")
    print("=" * 60)

    test_query = "강남구에 있는 국공립 어린이집 중 놀이터가 있는 곳 추천해줘"

    print(f"\n📝 Query: {test_query}\n")

    result = run_search_workflow_sync(test_query)

    print("\n" + "=" * 60)
    print("Workflow Results")
    print("=" * 60)

    print(f"\n1️⃣  Query Analysis:")
    print(f"   - Intent: {result.get('search_intent')}")
    print(f"   - Filters: {result.get('filters')}")
    print(f"   - Keywords: {result.get('keywords')}")

    print(f"\n2️⃣  Search Results:")
    results = result.get("search_results", [])
    print(f"   - Total: {len(results)}")
    if results:
        for i, r in enumerate(results[:3], 1):
            print(f"   - {i}. {r.get('crname')} ({r.get('crtypename')})")

    print(f"\n3️⃣  Generated Answer:")
    answer = result.get("answer", "")
    print(f"   {answer[:200]}..." if len(answer) > 200 else f"   {answer}")

    print(f"\n4️⃣  Metadata:")
    metadata = result.get("metadata", {})
    for key, value in metadata.items():
        if key != "result_summary":
            print(f"   - {key}: {value}")
