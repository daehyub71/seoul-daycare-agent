"""
Query Analyzer Node
Extracts intent, filters, and keywords from user query using LLM
"""

import json
import sys
from pathlib import Path
from typing import TypedDict
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from utils.prompts import QUERY_ANALYZER_PROMPT


class WorkflowState(TypedDict):
    """Workflow state structure"""

    query: str
    search_intent: str
    filters: dict
    keywords: list
    vector_results: list
    db_results: list
    search_results: list
    answer: str
    metadata: dict


def query_analyzer_node(state: WorkflowState) -> WorkflowState:
    """
    Analyze user query and extract intent, filters, and keywords

    Args:
        state: Current workflow state with 'query'

    Returns:
        Updated state with 'search_intent', 'filters', 'keywords'
    """
    query = state.get("query", "")

    if not query or not query.strip():
        return {
            **state,
            "search_intent": "unknown",
            "filters": {},
            "keywords": [],
            "metadata": {"analyzer_error": "Empty query"},
        }

    try:
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            model = settings.OPENAI_MODEL
        else:
            from openai import AzureOpenAI

            client = AzureOpenAI(
                api_key=settings.AOAI_API_KEY,
                api_version=settings.AOAI_API_VERSION,
                azure_endpoint=settings.AOAI_ENDPOINT,
            )
            model = settings.AOAI_DEPLOY_GPT4O

        # Call LLM to analyze query
        prompt = QUERY_ANALYZER_PROMPT.format(query=query)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a query analysis expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        # Parse response
        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        # Extract fields
        search_intent = result.get("search_intent", "unknown")
        filters = result.get("filters", {})
        keywords = result.get("keywords", [])

        print(f"[OK] Query analyzed:")
        print(f"   - Intent: {search_intent}")
        print(f"   - Filters: {filters}")
        print(f"   - Keywords: {keywords}")

        return {
            **state,
            "search_intent": search_intent,
            "filters": filters,
            "keywords": keywords,
        }

    except Exception as e:
        print(f"[WARN] Query analyzer error: {e}")
        return {
            **state,
            "search_intent": "unknown",
            "filters": {},
            "keywords": [],
            "metadata": {"analyzer_error": str(e)},
        }
