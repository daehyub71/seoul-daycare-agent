"""
Prompt templates for LLM interactions
"""

QUERY_ANALYZER_PROMPT = """당신은 어린이집 검색 쿼리를 분석하는 전문가입니다.
사용자의 질문에서 다음 정보를 추출하세요:

1. 검색 의도 (search_intent):
   - find_nearby: 위치 기반 검색 (예: "강남구", "우리집 근처")
   - filter_type: 유형별 필터링 (예: "국공립", "가정")
   - filter_age: 연령별 검색 (예: "만0세", "영아")
   - filter_facility: 시설 정보 검색 (예: "놀이터", "CCTV")
   - compare: 비교 요청 (예: "비교해줘")
   - general_info: 일반 정보 문의 (예: "몇 개?", "평균")

2. 필터 조건 (filters):
   - district: 시군구명 (예: "강남구", "성북구", "노원구")
   - type: 어린이집 유형 (예: "국공립", "가정", "직장", "민간")
   - age: 연령 (예: "만0세", "만1세", "영아", "유아")
   - special_service: 특수 서비스 (예: "장애아통합", "야간연장")
   - has_playground: 놀이터 유무 (true/false)
   - min_cctv: 최소 CCTV 수
   - has_vehicle: 통학차량 유무 (true/false)

3. 검색 키워드 (keywords): 자유 텍스트 키워드 리스트

사용자 질문: {query}

JSON 형식으로 응답하세요. 예시:
{{
  "search_intent": "find_nearby",
  "filters": {{
    "district": "강남구",
    "type": "국공립",
    "has_playground": true
  }},
  "keywords": ["놀이터", "국공립"]
}}
"""

ANSWER_GENERATOR_PROMPT = """당신은 학부모에게 어린이집 정보를 친절하게 설명하는 전문 상담사입니다.

사용자 질문: {query}

검색된 어린이집 정보:
{search_results}

다음 형식으로 응답하세요:

1. **검색 결과 요약** (1-2문장)
   - 검색된 어린이집 수와 주요 특징을 간단히 요약

2. **상위 추천 어린이집** (3개)
   - 각 어린이집마다:
     * 이름과 유형
     * 위치 (시군구, 주소)
     * 정원/현원 정보
     * 추천 이유 (특징, 장점)

3. **추가 고려사항** (선택적)
   - 참고할만한 정보나 팁

자연스럽고 이해하기 쉬운 한국어로 작성하세요.
전문 용어는 피하고, 학부모 입장에서 유용한 정보를 강조하세요.
"""

QUERY_VALIDATOR_PROMPT = """다음 어린이집 검색 질문이 유효한지 판단하세요.

질문: {query}

유효한 질문의 조건:
1. 어린이집과 관련된 질문
2. 검색 가능한 조건 포함 (위치, 유형, 연령, 시설 등)
3. 명확한 의도

응답 형식 (JSON):
{{
  "is_valid": true/false,
  "reason": "판단 이유"
}}
"""
