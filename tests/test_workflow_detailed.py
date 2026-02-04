"""
Detailed Workflow Test
Tests the complete LangGraph workflow with multiple scenarios
"""

import sys
from pathlib import Path
import json

# Add app directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

from workflows.graph_builder import run_search_workflow_sync

print("=" * 60)
print("Detailed Workflow Tests")
print("=" * 60)

# Test scenarios
test_cases = [
    {
        "name": "위치 + 유형 검색",
        "query": "강남구 국공립 어린이집 추천해줘",
        "expected_filters": ["district", "type"],
    },
    {
        "name": "시설 조건 검색",
        "query": "놀이터가 있는 어린이집 찾아줘",
        "expected_filters": ["has_playground"],
    },
    {
        "name": "다중 조건 검색",
        "query": "송파구에 있는 직장 어린이집 중 CCTV가 많은 곳",
        "expected_filters": ["district", "type"],
    },
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Test Case {i}: {test_case['name']}")
    print(f"{'='*60}")

    query = test_case["query"]
    print(f"\n📝 Query: {query}")

    try:
        # Run workflow
        result = run_search_workflow_sync(query)

        # Display results
        print(f"\n1️⃣  Query Analysis:")
        print(f"   Intent: {result.get('search_intent', 'N/A')}")
        print(f"   Filters: {json.dumps(result.get('filters', {}), ensure_ascii=False, indent=6)}")
        print(f"   Keywords: {result.get('keywords', [])}")

        print(f"\n2️⃣  Retrieval:")
        results = result.get("search_results", [])
        print(f"   Found: {len(results)} daycare centers")

        if results:
            print(f"\n   Top 3 Results:")
            for j, r in enumerate(results[:3], 1):
                print(f"   {j}. {r.get('crname')} ({r.get('crtypename')})")
                print(f"      - 위치: {r.get('sigunname')} - {r.get('craddr', '')[:40]}...")
                print(f"      - 정원/현원: {r.get('crcapat')}/{r.get('crchcnt')}")
                if r.get('plgrdco', 0) > 0:
                    print(f"      - 놀이터: ✓")
                if r.get('cctvinstlcnt', 0) > 0:
                    print(f"      - CCTV: {r.get('cctvinstlcnt')}대")

        print(f"\n3️⃣  Generated Answer:")
        answer = result.get("answer", "")
        lines = answer.split("\n")
        for line in lines[:10]:  # First 10 lines
            print(f"   {line}")
        if len(lines) > 10:
            print(f"   ... ({len(lines)-10} more lines)")

        print(f"\n4️⃣  Metadata:")
        metadata = result.get("metadata", {})
        print(f"   - Total results: {metadata.get('total_results', 0)}")
        print(f"   - Answer length: {metadata.get('answer_length', 0)} chars")
        print(f"   - Filters applied: {metadata.get('filters_applied', [])}")

        print(f"\n✅ Test case {i} completed successfully")

    except Exception as e:
        print(f"\n❌ Test case {i} failed: {e}")
        import traceback

        traceback.print_exc()

print(f"\n{'='*60}")
print("✅ All Workflow Tests Complete")
print(f"{'='*60}")
