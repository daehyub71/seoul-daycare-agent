"""
Seoul Daycare Search AI - Streamlit UI
Main application interface
"""

import sys
from pathlib import Path
import streamlit as st
import requests

# Add app directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

# Page config
st.set_page_config(
    page_title="서울시 어린이집 검색 AI",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e3f2fd;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-header">🏫 서울시 어린이집 검색 AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI 기반 맞춤형 어린이집 검색 서비스</div>',
    unsafe_allow_html=True,
)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_daycares" not in st.session_state:
    st.session_state.selected_daycares = []

# Sidebar - Filters
with st.sidebar:
    st.header("🔍 검색 옵션")

    # District filter
    st.subheader("시군구")
    try:
        response = requests.get("http://localhost:8000/api/v1/districts")
        if response.status_code == 200:
            districts_data = response.json()
            district_options = ["전체"] + [d["name"] for d in districts_data["districts"]]
            selected_district = st.selectbox(
                "시군구 선택",
                district_options,
                key="district_filter",
                label_visibility="collapsed",
            )
        else:
            selected_district = st.text_input("시군구명 입력", key="district_text")
    except:
        selected_district = st.text_input("시군구명 입력", key="district_text")

    # Type filter
    st.subheader("어린이집 유형")
    try:
        response = requests.get("http://localhost:8000/api/v1/types")
        if response.status_code == 200:
            types_data = response.json()
            type_options = ["전체"] + [t["name"] for t in types_data["types"]]
            selected_type = st.selectbox(
                "유형 선택",
                type_options,
                key="type_filter",
                label_visibility="collapsed",
            )
        else:
            selected_type = st.text_input("유형 입력", key="type_text")
    except:
        selected_type = st.text_input("유형 입력", key="type_text")

    # Facility filters
    st.subheader("시설 조건")
    has_playground = st.checkbox("놀이터 있음", key="playground_filter")
    min_cctv = st.slider("최소 CCTV 수", 0, 50, 0, key="cctv_filter")

    # Age filter
    st.subheader("연령")
    age_options = st.multiselect(
        "연령 선택",
        ["만0세", "만1세", "만2세", "만3세", "만4세", "만5세"],
        key="age_filter",
    )

    st.divider()

    # Statistics
    st.subheader("📊 전체 통계")
    try:
        response = requests.get("http://localhost:8000/api/v1/stats")
        if response.status_code == 200:
            stats = response.json()
            st.metric("전체 어린이집", f"{stats['total']:,}개")

            with st.expander("시군구별 통계"):
                for d in stats["by_district"][:5]:
                    st.text(f"{d['name']}: {d['count']:,}개")

            with st.expander("유형별 통계"):
                for t in stats["by_type"]:
                    st.text(f"{t['name']}: {t['count']:,}개")
    except:
        st.info("서버에 연결할 수 없습니다.")

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 자연어 검색")
    query = st.text_input(
        "어떤 어린이집을 찾으시나요?",
        placeholder="예: 강남구에 있는 국공립 어린이집 추천해줘",
        key="query_input",
    )

with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    search_button = st.button("🔍 검색", type="primary", use_container_width=True)

# Search logic
if search_button and query:
    with st.spinner("검색 중..."):
        try:
            # Build filters
            filters = {}
            if selected_district and selected_district != "전체":
                filters["district"] = selected_district
            if selected_type and selected_type != "전체":
                filters["type"] = selected_type
            if has_playground:
                filters["has_playground"] = True
            if min_cctv > 0:
                filters["min_cctv"] = min_cctv
            if age_options:
                filters["age"] = " ".join(age_options)

            # Call API
            response = requests.post(
                "http://localhost:8000/api/v1/search",
                json={"query": query, "filters": filters},
                timeout=30,
            )

            if response.status_code == 200:
                st.session_state.search_results = response.json()
                st.success("검색 완료!")
            else:
                st.error(f"검색 실패: {response.json().get('detail', '알 수 없는 오류')}")

        except requests.exceptions.ConnectionError:
            st.error("서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요.")
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")

# Display results
if st.session_state.search_results:
    results = st.session_state.search_results

    st.divider()

    # AI Answer
    st.subheader("🤖 AI 추천")
    st.markdown(results.get("answer", ""))

    st.divider()

    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 리스트", "🗺️ 지도", "⚖️ 비교", "📊 통계"])

    with tab1:
        st.subheader(f"검색 결과 ({results.get('total', 0)}개)")

        daycare_list = results.get("results", [])

        if daycare_list:
            for i, daycare in enumerate(daycare_list, 1):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.markdown(f"### {i}. {daycare.get('crname', 'N/A')}")
                        st.caption(f"**유형:** {daycare.get('crtypename', 'N/A')}")
                        st.caption(f"**주소:** {daycare.get('sigunname', 'N/A')} - {daycare.get('craddr', 'N/A')[:50]}...")

                    with col2:
                        st.metric("정원", f"{daycare.get('crcapat', 0)}명")
                        st.metric("현원", f"{daycare.get('crchcnt', 0)}명")

                    with col3:
                        if daycare.get("plgrdco", 0) > 0:
                            st.success("🎡 놀이터")
                        if daycare.get("cctvinstlcnt", 0) > 0:
                            st.info(f"📹 CCTV {daycare.get('cctvinstlcnt')}대")

                        # Compare checkbox
                        if st.checkbox(
                            "비교",
                            key=f"compare_{daycare.get('stcode')}",
                            value=daycare.get("stcode") in st.session_state.selected_daycares,
                        ):
                            if daycare.get("stcode") not in st.session_state.selected_daycares:
                                st.session_state.selected_daycares.append(daycare.get("stcode"))
                        else:
                            if daycare.get("stcode") in st.session_state.selected_daycares:
                                st.session_state.selected_daycares.remove(daycare.get("stcode"))

                    st.divider()
        else:
            st.info("검색 결과가 없습니다.")

    with tab2:
        st.subheader("🗺️ 지도")
        # Map visualization will be implemented in components
        st.info("지도 시각화 기능은 구현 예정입니다.")

        # Simple coordinate display
        daycare_list = results.get("results", [])
        valid_coords = [
            (d.get("la"), d.get("lo"), d.get("crname"))
            for d in daycare_list
            if d.get("la") and d.get("lo")
        ]

        if valid_coords:
            import pandas as pd

            df = pd.DataFrame(valid_coords, columns=["lat", "lon", "name"])
            st.map(df)
        else:
            st.warning("좌표 정보가 없는 결과입니다.")

    with tab3:
        st.subheader("⚖️ 비교")

        if len(st.session_state.selected_daycares) >= 2:
            st.info(f"{len(st.session_state.selected_daycares)}개 어린이집 선택됨")

            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/compare",
                    params={"stcodes": st.session_state.selected_daycares},
                )

                if response.status_code == 200:
                    compare_data = response.json()
                    daycares = compare_data.get("daycares", [])

                    # Comparison table
                    import pandas as pd

                    df = pd.DataFrame(
                        {
                            "이름": [d.get("crname") for d in daycares],
                            "유형": [d.get("crtypename") for d in daycares],
                            "시군구": [d.get("sigunname") for d in daycares],
                            "정원": [d.get("crcapat") for d in daycares],
                            "현원": [d.get("crchcnt") for d in daycares],
                            "보육실": [d.get("nrtrroomcnt") for d in daycares],
                            "놀이터": [d.get("plgrdco") for d in daycares],
                            "CCTV": [d.get("cctvinstlcnt") for d in daycares],
                            "전화": [d.get("crtelno") for d in daycares],
                        }
                    )

                    st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"비교 오류: {e}")

        else:
            st.info("비교하려면 리스트 탭에서 2개 이상의 어린이집을 선택하세요.")

    with tab4:
        st.subheader("📊 통계")

        daycare_list = results.get("results", [])

        if daycare_list:
            import pandas as pd

            # Type distribution
            type_counts = pd.DataFrame(daycare_list)["crtypename"].value_counts()
            st.bar_chart(type_counts)

            # Capacity statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_capacity = sum(d.get("crcapat", 0) for d in daycare_list) / len(daycare_list)
                st.metric("평균 정원", f"{avg_capacity:.0f}명")
            with col2:
                avg_current = sum(d.get("crchcnt", 0) for d in daycare_list) / len(daycare_list)
                st.metric("평균 현원", f"{avg_current:.0f}명")
            with col3:
                with_playground = sum(1 for d in daycare_list if d.get("plgrdco", 0) > 0)
                st.metric("놀이터 보유", f"{with_playground}개소")

# Footer
st.divider()
st.caption("© 2026 Seoul Daycare Search AI | Powered by OpenAI & LangGraph")
