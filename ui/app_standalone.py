"""
Seoul Daycare Search AI - Streamlit UI (Standalone)
Standalone version for Streamlit Cloud deployment
"""

import sys
import os
from pathlib import Path
import streamlit as st

# Add app directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

# Set environment variables from Streamlit secrets (for Cloud deployment)
if hasattr(st, 'secrets'):
    for key in st.secrets:
        os.environ[key] = str(st.secrets[key])

# Import workflow components
from workflows.graph_builder import SearchWorkflow
from database import get_session, DaycareCenter

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

# Initialize workflow
@st.cache_resource
def get_workflow():
    """Initialize and cache workflow"""
    return SearchWorkflow()

workflow = get_workflow()

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_daycares" not in st.session_state:
    st.session_state.selected_daycares = []

# Sidebar - Filters
with st.sidebar:
    st.header("🔍 검색 옵션")

    # Get districts from database
    session = get_session()
    try:
        districts = session.query(DaycareCenter.sigunname).distinct().filter(
            DaycareCenter.crstatusname == "정상"
        ).all()
        district_options = ["전체"] + sorted([d[0] for d in districts if d[0]])
    except:
        district_options = ["전체"]
    finally:
        session.close()

    selected_district = st.selectbox("시군구", district_options, key="district_filter")

    # Type filter
    st.subheader("어린이집 유형")
    session = get_session()
    try:
        types = session.query(DaycareCenter.crtypename).distinct().filter(
            DaycareCenter.crstatusname == "정상"
        ).all()
        type_options = ["전체"] + sorted([t[0] for t in types if t[0]])
    except:
        type_options = ["전체"]
    finally:
        session.close()

    selected_type = st.selectbox("유형", type_options, key="type_filter")

    # Facility filters
    st.subheader("시설 조건")
    has_playground = st.checkbox("놀이터 있음", key="playground_filter")
    min_cctv = st.slider("최소 CCTV 수", 0, 50, 0, key="cctv_filter")

    # Statistics
    st.divider()
    st.subheader("📊 전체 통계")
    session = get_session()
    try:
        total = session.query(DaycareCenter).filter(
            DaycareCenter.crstatusname == "정상"
        ).count()
        st.metric("전체 어린이집", f"{total:,}개")
    except:
        st.info("통계를 불러올 수 없습니다.")
    finally:
        session.close()

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
    st.write("")
    st.write("")
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

            # Run workflow
            result = workflow.run(query=query, filters=filters)

            # Store results
            st.session_state.search_results = {
                "answer": result.get("answer", ""),
                "results": result.get("search_results", []),
                "total": len(result.get("search_results", []))
            }
            st.success("검색 완료!")

        except Exception as e:
            st.error(f"검색 오류: {str(e)}")

# Display results
if st.session_state.search_results:
    results = st.session_state.search_results

    st.divider()

    # AI Answer
    st.subheader("🤖 AI 추천")
    st.markdown(results.get("answer", ""))

    st.divider()

    # Results tabs
    tab1, tab2 = st.tabs(["📋 리스트", "📊 통계"])

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
                            st.success("놀이터")
                        if daycare.get("cctvinstlcnt", 0) > 0:
                            st.info(f"CCTV {daycare.get('cctvinstlcnt')}대")

                    st.divider()
        else:
            st.info("검색 결과가 없습니다.")

    with tab2:
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
