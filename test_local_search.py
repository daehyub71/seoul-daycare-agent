"""
로컬 검색 테스트 스크립트
간단하게 검색 기능을 테스트할 수 있습니다.
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from workflows.graph_builder import run_search_workflow_sync

def test_search(query: str, filters: dict = None):
    """검색 테스트"""
    print("=" * 70)
    print(f"[QUERY] {query}")
    if filters:
        print(f"[FILTER] {filters}")
    print("=" * 70)

    try:
        # Run search
        result = run_search_workflow_sync(query, filters)

        # Show results
        results = result.get("search_results", [])
        print(f"\n[OK] 검색 완료: 총 {len(results)}개 결과")

        if results:
            print("\n" + "=" * 70)
            print("검색 결과:")
            print("=" * 70)
            for i, r in enumerate(results[:10], 1):
                print(f"\n{i}. {r.get('crname', 'N/A')}")
                print(f"   위치: {r.get('sigunname', 'N/A')}")
                print(f"   유형: {r.get('crtypename', 'N/A')}")
                print(f"   정원/현원: {r.get('crcapat', 0)}명 / {r.get('crchcnt', 0)}명")
                if r.get('plgrdco', 0) > 0:
                    print(f"   놀이터: O")
                if r.get('cctvinstlcnt', 0) > 0:
                    print(f"   CCTV: {r.get('cctvinstlcnt')}대")

            # Show AI answer
            answer = result.get("answer", "")
            if answer:
                print("\n" + "=" * 70)
                print("AI 추천:")
                print("=" * 70)
                print(answer)
        else:
            print("\n[ERROR] 검색 조건에 맞는 어린이집이 없습니다.")
            print(f"Metadata: {result.get('metadata')}")

    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 테스트 케이스들

    print("\n[TEST 1] 기본 검색 (필터 없음)")
    test_search("강남구 어린이집 추천해줘")

    print("\n\n[TEST 2] 시군구 필터")
    test_search("어린이집 추천해줘", {"district": "강남구"})

    print("\n\n[TEST 3] 시군구 + 유형 필터")
    test_search("어린이집 추천해줘", {"district": "강남구", "type": "국공립"})

    print("\n\n[TEST 4] 놀이터 필터")
    test_search("강남구 어린이집", {"district": "강남구", "has_playground": True})

    print("\n" + "=" * 70)
    print("[OK] 모든 테스트 완료!")
    print("=" * 70)
