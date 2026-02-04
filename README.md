# Seoul Daycare Search & Recommendation AI Service

서울시 어린이집 정보를 활용한 AI 기반 검색/추천 서비스

## 프로젝트 개요

학부모가 자연어 질문으로 조건에 맞는 어린이집을 검색하고 AI 추천을 받을 수 있는 RAG 기반 서비스입니다.

### 주요 기능

- **자연어 검색**: "강남구 국공립 어린이집 추천해줘"
- **위치 기반 검색**: 좌표, 시군구 필터링
- **유형/특성 필터**: 국공립, 가정, 직장, 장애아통합, 야간연장 등
- **연령별 검색**: 만0세~만5세 반 운영 정보
- **시설 정보**: 보육실, 놀이터, CCTV 등
- **다양한 결과 표시**: AI 요약 + 카드 리스트 + 지도 시각화 + 비교 테이블

## 기술 스택

### Backend
- **Framework**: FastAPI 0.104+
- **Orchestration**: LangGraph (LangChain)
- **LLM**: OpenAI GPT-4o-mini
- **Embedding**: text-embedding-3-large (3072차원)
- **Vector DB**: FAISS (IndexFlatL2)
- **Database**: SQLite + SQLAlchemy

### Frontend
- **Framework**: Streamlit
- **Visualization**: Matplotlib, Plotly

## 프로젝트 구조

```
seoul-daycare-agent/
├── app/                    # FastAPI 백엔드
│   ├── main.py            # 메인 애플리케이션
│   ├── config.py          # 환경 설정
│   ├── database/          # DB 모델 및 연결
│   ├── services/          # 임베딩, 벡터 스토어 등
│   ├── workflows/         # LangGraph 워크플로우
│   ├── api/               # API 라우트
│   └── utils/             # 유틸리티 (프롬프트 등)
├── ui/                    # Streamlit 프론트엔드
│   ├── app.py            # 메인 UI
│   └── components/       # UI 컴포넌트
├── data/                  # 데이터 디렉토리
│   ├── raw/              # 원본 데이터
│   ├── processed/        # SQLite DB
│   └── vector_index/     # FAISS 인덱스
├── scripts/               # 유틸리티 스크립트
│   ├── preprocess_data.py
│   └── create_index.py
└── tests/                 # 테스트 코드
```

## LangGraph 워크플로우 (4단계)

```
사용자 질문
    ↓
Query Analyzer (의도/키워드/필터 추출)
    ↓
Document Retriever (FAISS + SQLite 하이브리드 검색)
    ↓
Answer Generator (GPT-4o-mini로 자연어 요약)
    ↓
Post Processor (품질 검증 및 메타데이터 추가)
    ↓
결과 반환
```

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 루트 디렉토리에 생성하거나 기존 `.env` 사용:

```bash
# Azure OpenAI Configuration
AOAI_API_KEY=<your-api-key>
AOAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AOAI_API_VERSION=2024-05-01-preview
AOAI_DEPLOY_GPT4O=gpt-4o-mini
AOAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Database & Vector Index
DB_PATH=data/processed/daycare.db
VECTOR_INDEX_PATH=data/vector_index/faiss.index
```

### 3. 데이터 준비

```bash
# 데이터 전처리 (JSON → SQLite)
python scripts/preprocess_data.py

# 벡터 인덱스 생성
python scripts/create_index.py
```

### 4. 서비스 실행

**FastAPI 백엔드:**
```bash
cd app
uvicorn main:app --reload --port 8000
```

**Streamlit 프론트엔드:**
```bash
streamlit run ui/app.py
```

## API 엔드포인트

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/search` | 어린이집 검색 |
| GET | `/api/v1/daycares/{stcode}` | 어린이집 상세 정보 |
| POST | `/api/v1/compare` | 어린이집 비교 |
| GET | `/api/v1/districts` | 시군구 목록 |
| GET | `/api/v1/types` | 어린이집 유형 목록 |

## 사용 예시

### 검색 API 요청

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "성북구 국공립 어린이집 중 놀이터 있는 곳",
    "filters": {
      "district": "성북구",
      "type": "국공립",
      "has_playground": true
    }
  }'
```

### 응답 예시

```json
{
  "summary": "성북구의 국공립 어린이집 중 놀이터가 있는 곳을 찾았습니다. 총 3개가 검색되었으며...",
  "results": [
    {
      "stcode": "11290000666",
      "crname": "구립벤처타운어린이집",
      "crtypename": "국공립",
      "craddr": "서울특별시 성북구...",
      "crcapat": 45,
      "crchcnt": 17,
      "plgrdco": 1,
      "cctvinstlcnt": 16
    }
  ],
  "total": 3
}
```

## 테스트

```bash
# 전체 테스트 실행
pytest tests/ -v

# 특정 테스트
pytest tests/test_workflow.py -v
```

## 개발 단계

- [x] Phase 1: 데이터 준비 및 인프라 구축
  - [x] 프로젝트 구조 생성
  - [ ] 환경 설정
  - [ ] 데이터 전처리
  - [ ] SQLite DB 생성
  - [ ] FAISS 인덱스 생성
- [ ] Phase 2: Backend 개발
  - [ ] FastAPI 기본 구조
  - [ ] LangGraph 워크플로우 구현
  - [ ] API 라우트 구현
- [ ] Phase 3: Frontend 개발
  - [ ] Streamlit UI 구현
  - [ ] 컴포넌트 개발
- [ ] Phase 4: 테스트 및 최적화
  - [ ] 단위 테스트
  - [ ] 통합 테스트
  - [ ] 성능 최적화

## 문서

- [상세 개발 계획서](docs/개발계획서.md)
- [데이터베이스 스키마](docs/개발계획서.md#41-sqlite-데이터베이스-스키마)
- [API 명세](docs/개발계획서.md#52-주요-api-엔드포인트)

## 참고 프로젝트

이 프로젝트는 다음 기존 프로젝트들의 패턴을 참고했습니다:
- [Government Document AI Search](../government-doc-ai-langgraph/) - 4단계 LangGraph 워크플로우
- [Seoul Night Spots Agent](../06943_63_c06aee0e-9a58-4814-9737-ce1f3233c5c7/) - 위치 기반 검색 및 시각화
- [Customer Support MCP System](../customer-support-mcp-system/) - RAG 파이프라인

## 라이선스

MIT License

## 문의

이슈나 질문은 GitHub Issues를 활용해주세요.
