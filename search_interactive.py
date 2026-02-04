"""
대화형 검색 테스트
직접 검색어를 입력하고 결과를 확인할 수 있습니다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))

from workflows.graph_builder import run_search_workflow_sync

def main():
    print("=" * 70)
    print("[INFO] 서울시 어린이집 검색 AI - 로컬 테스트")
    print("=" * 70)
    print()
    print("사용 방법:")
    print("  1. 검색어만 입력: 강남구 어린이집 추천해줘")
    print("  2. 종료: 'quit' 또는 'exit' 입력")
    print()

    while True:
        print("-" * 70)
        query = input("\n[SEARCH] 검색어를 입력하세요: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("\n[EXIT] 종료합니다.")
            break

        if not query:
            print("[ERROR] 검색어를 입력해주세요.")
            continue

        # Ask for filters
        print("\n필터를 설정하시겠습니까? (y/n): ", end="")
        use_filters = input().strip().lower()

        filters = {}
        if use_filters == 'y':
            district = input("  시군구 (예: 강남구, 없으면 Enter): ").strip()
            if district:
                filters["district"] = district

            dtype = input("  유형 (예: 국공립, 없으면 Enter): ").strip()
            if dtype:
                filters["type"] = dtype

            playground = input("  놀이터 필요? (y/n): ").strip().lower()
            if playground == 'y':
                filters["has_playground"] = True

        print("\n[PROCESSING] 검색 중...")
        print("=" * 70)

        try:
            result = run_search_workflow_sync(query, filters if filters else None)
            results = result.get("search_results", [])

            print(f"\n[OK] 검색 완료: 총 {len(results)}개")

            if results:
                print("\n[RESULTS] 검색 결과:")
                for i, r in enumerate(results[:5], 1):
                    print(f"\n  {i}. {r.get('crname', 'N/A')}")
                    print(f"     위치: {r.get('sigunname', 'N/A')} - {r.get('craddr', 'N/A')[:40]}...")
                    print(f"     유형: {r.get('crtypename', 'N/A')}")
                    print(f"     정원/현원: {r.get('crcapat', 0)}명 / {r.get('crchcnt', 0)}명")

                if len(results) > 5:
                    print(f"\n  ... 외 {len(results) - 5}개")

                # AI Answer
                answer = result.get("answer", "")
                if answer:
                    print("\n" + "=" * 70)
                    print("[AI] 추천:")
                    print("=" * 70)
                    print(answer[:500] + "..." if len(answer) > 500 else answer)
            else:
                print("\n[ERROR] 검색 조건에 맞는 어린이집이 없습니다.")

        except Exception as e:
            print(f"\n[ERROR] 오류 발생: {e}")

        print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
