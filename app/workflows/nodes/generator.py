"""
Answer Generator Node
Generates natural language answer from search results using LLM
"""

import json
import sys
from pathlib import Path
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from utils.prompts import ANSWER_GENERATOR_PROMPT


def format_search_results(results: list) -> str:
    """Format search results for LLM"""
    if not results:
        return "검색 결과가 없습니다."

    formatted = []
    for i, result in enumerate(results[:10], 1):  # Limit to top 10
        item = f"""
어린이집 {i}:
- 이름: {result.get('crname', 'N/A')}
- 유형: {result.get('crtypename', 'N/A')}
- 시군구: {result.get('sigunname', 'N/A')}
- 주소: {result.get('craddr', 'N/A')}
- 정원/현원: {result.get('crcapat', 0)}명 / {result.get('crchcnt', 0)}명
- 보육실: {result.get('nrtrroomcnt', 0)}개
- 놀이터: {'있음' if result.get('plgrdco', 0) > 0 else '없음'}
- CCTV: {result.get('cctvinstlcnt', 0)}대
- 특수서비스: {result.get('crspec', '')}
- 전화번호: {result.get('crtelno', 'N/A')}
"""
        formatted.append(item.strip())

    return "\n\n".join(formatted)


def answer_generator_node(state: dict) -> dict:
    """
    Generate natural language answer from search results

    Args:
        state: Workflow state with 'query', 'search_results'

    Returns:
        Updated state with 'answer'
    """
    query = state.get("query", "")
    search_results = state.get("search_results", [])

    if not search_results:
        return {
            **state,
            "answer": "죄송합니다. 검색 조건에 맞는 어린이집을 찾지 못했습니다. 다른 조건으로 검색해보시겠어요?",
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

        # Format search results
        formatted_results = format_search_results(search_results)

        # Generate answer
        prompt = ANSWER_GENERATOR_PROMPT.format(
            query=query, search_results=formatted_results
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful daycare information consultant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        answer = response.choices[0].message.content

        print(f"\n[OK] Answer generated ({len(answer)} chars)")

        return {
            **state,
            "answer": answer,
        }

    except Exception as e:
        print(f"[WARN] Answer generator error: {e}")
        # Fallback answer
        answer = f"""검색 결과 {len(search_results)}개의 어린이집을 찾았습니다.

상위 3개 추천:
"""
        for i, result in enumerate(search_results[:3], 1):
            answer += f"\n{i}. {result.get('crname')} ({result.get('crtypename')})"
            answer += f"\n   위치: {result.get('sigunname')} - {result.get('craddr')}"
            answer += f"\n   정원/현원: {result.get('crcapat')}명 / {result.get('crchcnt')}명\n"

        return {
            **state,
            "answer": answer,
            "metadata": {
                **state.get("metadata", {}),
                "generator_error": str(e),
            },
        }
