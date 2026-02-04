# 로컬 테스트 가이드

## 사용 가능한 테스트 스크립트

### 1. test_local_search.py - 자동 테스트
여러 검색 시나리오를 자동으로 테스트합니다.

```bash
python test_local_search.py
```

**테스트 항목:**
- 테스트 1: 기본 검색 (필터 없음) - "강남구 어린이집 추천해줘"
- 테스트 2: 시군구 필터 - district="강남구"
- 테스트 3: 시군구 + 유형 필터 - district="강남구", type="국공립"
- 테스트 4: 놀이터 필터 - district="강남구", has_playground=True

### 2. search_interactive.py - 대화형 테스트
직접 검색어를 입력하며 테스트할 수 있습니다.

```bash
python search_interactive.py
```

**사용 방법:**
1. 프로그램 실행
2. 검색어 입력 (예: "강남구 어린이집 추천해줘")
3. 필터 설정 여부 선택 (y/n)
4. 필터 선택 시 상세 조건 입력:
   - 시군구 (예: 강남구)
   - 유형 (예: 국공립)
   - 놀이터 필요 여부 (y/n)
5. 결과 확인
6. 종료하려면 'quit' 또는 'exit' 입력

## 필터 옵션

### 시군구 (district)
- 강남구, 서초구, 성북구 등
- 예: `{"district": "강남구"}`

### 유형 (type)
- 국공립, 민간, 가정, 직장 등
- 예: `{"type": "국공립"}`

### 놀이터 (has_playground)
- 놀이터가 있는 어린이집만 검색
- 예: `{"has_playground": True}`

### CCTV (min_cctv)
- 최소 CCTV 대수
- 예: `{"min_cctv": 10}`

### 복합 필터 예시
```python
filters = {
    "district": "강남구",
    "type": "국공립",
    "has_playground": True,
    "min_cctv": 5
}
result = run_search_workflow_sync("어린이집 추천해줘", filters)
```

## 환경 설정 확인

테스트를 실행하기 전에 다음을 확인하세요:

1. **.env 파일 존재 여부**
   ```
   OPENAI_API_KEY=your-key-here
   ```
   또는
   ```
   AOAI_API_KEY=your-azure-key
   AOAI_ENDPOINT=https://your-resource.openai.azure.com/
   AOAI_API_VERSION=2024-05-01-preview
   AOAI_DEPLOY_GPT4O=gpt-4o-mini
   AOAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
   ```

2. **데이터 파일 존재 여부**
   - `data/processed/daycare.db`
   - `data/vector_index/faiss.index`
   - `data/vector_index/metadata.json`

3. **의존성 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

## 문제 해결

### 1. ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 파일 없음
```bash
python scripts/preprocess_data.py
python scripts/create_index.py
```

### 3. API 키 오류
`.env` 파일에 올바른 API 키가 설정되어 있는지 확인하세요.

### 4. 검색 결과 0개
- 필터 조건이 너무 엄격한지 확인
- 해당 지역에 어린이집이 있는지 데이터베이스 확인
- 벡터 인덱스가 제대로 생성되었는지 확인

## 출력 예시

```
[TEST 1] 기본 검색 (필터 없음)
======================================================================
[QUERY] 강남구 어린이집 추천해줘
======================================================================

[OK] Query analyzed:
   - Intent: find_nearby
   - Filters: {'district': '강남구'}
   - Keywords: ['어린이집', '추천']

[SEARCH] Starting retrieval...
   [OK] Vector search: 20 candidates
   [OK] Database filter: 10 results

[OK] Answer generated (858 chars)

[OK] 검색 완료: 총 10개 결과

======================================================================
검색 결과:
======================================================================

1. 강남영재어린이집
   위치: 강남구
   유형: 민간
   정원/현원: 45명 / 42명
   CCTV: 16대

2. 강남센트럴어린이집
   위치: 강남구
   유형: 민간
   정원/현원: 62명 / 58명
   놀이터: O
   CCTV: 20대

...
```

## 추가 정보

- 검색 결과는 벡터 유사도와 데이터베이스 필터를 결합한 하이브리드 검색으로 생성됩니다.
- AI 답변은 OpenAI GPT-4o-mini 모델로 생성됩니다.
- TOP_K 설정에 따라 최대 10개의 결과가 반환됩니다.
