"""
Post Processor Node
Validates and enhances the final answer
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def post_processor_node(state: dict) -> dict:
    """
    Post-process the answer and add metadata

    Args:
        state: Workflow state with 'answer', 'search_results'

    Returns:
        Updated state with enhanced 'answer' and 'metadata'
    """
    answer = state.get("answer", "")
    search_results = state.get("search_results", [])
    metadata = state.get("metadata", {})

    # Validate answer
    if not answer or len(answer) < 10:
        answer = "죄송합니다. 답변 생성에 문제가 발생했습니다. 다시 시도해주세요."

    # Add metadata
    metadata.update(
        {
            "total_results": len(search_results),
            "answer_length": len(answer),
            "has_results": len(search_results) > 0,
        }
    )

    # Extract result summaries for quick reference
    if search_results:
        result_summary = [
            {
                "stcode": r.get("stcode"),
                "crname": r.get("crname"),
                "crtypename": r.get("crtypename"),
                "sigunname": r.get("sigunname"),
                "crcapat": r.get("crcapat"),
                "crchcnt": r.get("crchcnt"),
                "crtelno": r.get("crtelno"),
            }
            for r in search_results[:5]  # Top 5
        ]
        metadata["result_summary"] = result_summary

    print(f"\n[OK] Post-processing complete")
    print(f"   - Total results: {len(search_results)}")
    print(f"   - Answer length: {len(answer)} chars")

    return {
        **state,
        "answer": answer,
        "metadata": metadata,
    }
