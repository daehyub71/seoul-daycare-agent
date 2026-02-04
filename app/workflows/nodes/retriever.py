"""
Document Retriever Node
Performs hybrid search (FAISS vector + SQLite filter)
"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from database import get_session, DaycareCenter
from services import get_vector_store
from sqlalchemy import and_, or_


def document_retriever_node(state: dict) -> dict:
    """
    Retrieve relevant daycare centers using hybrid search

    Args:
        state: Workflow state with 'query', 'filters', 'keywords'

    Returns:
        Updated state with 'search_results'
    """
    query = state.get("query", "")
    filters = state.get("filters", {})
    keywords = state.get("keywords", [])

    # Combine query and keywords for vector search
    search_text = query
    if keywords:
        search_text = f"{query} {' '.join(keywords)}"

    print(f"\n[SEARCH] Starting retrieval...")
    print(f"   - Query: {query}")
    print(f"   - Filters: {filters}")

    try:
        # Step 1: Vector similarity search (if index exists)
        vector_stcodes = set()
        vector_store = get_vector_store()

        if vector_store.index is not None:
            top_k = settings.TOP_K * 2  # Get more results for filtering
            vector_results = vector_store.search(search_text, top_k=top_k)
            vector_stcodes = {stcode for stcode, _ in vector_results}
            print(f"   [OK] Vector search: {len(vector_stcodes)} candidates")

        # Step 2: Database filtering
        session = get_session()

        # Build filter conditions
        conditions = []

        # Status filter (only active daycares)
        conditions.append(DaycareCenter.crstatusname == "정상")

        # District filter
        if filters.get("district"):
            conditions.append(DaycareCenter.sigunname.like(f"%{filters['district']}%"))

        # Type filter
        if filters.get("type"):
            type_name = filters["type"]
            conditions.append(DaycareCenter.crtypename.like(f"%{type_name}%"))

        # Age filter (check if class exists for specific age)
        age = filters.get("age")
        if age:
            age_conditions = []
            if "만0세" in age or "영아" in age:
                age_conditions.append(DaycareCenter.class_cnt_00 > 0)
            if "만1세" in age or "영아" in age:
                age_conditions.append(DaycareCenter.class_cnt_01 > 0)
            if "만2세" in age or "영아" in age:
                age_conditions.append(DaycareCenter.class_cnt_02 > 0)
            if "만3세" in age or "유아" in age:
                age_conditions.append(DaycareCenter.class_cnt_03 > 0)
            if "만4세" in age or "유아" in age:
                age_conditions.append(DaycareCenter.class_cnt_04 > 0)
            if "만5세" in age or "유아" in age:
                age_conditions.append(DaycareCenter.class_cnt_05 > 0)

            if age_conditions:
                conditions.append(or_(*age_conditions))

        # Facility filters
        if filters.get("has_playground"):
            conditions.append(DaycareCenter.plgrdco > 0)

        if filters.get("min_cctv"):
            min_cctv = int(filters["min_cctv"])
            conditions.append(DaycareCenter.cctvinstlcnt >= min_cctv)

        if filters.get("has_vehicle"):
            conditions.append(DaycareCenter.crcargbname.isnot(None))

        # Special service filter
        special_service = filters.get("special_service")
        if special_service:
            conditions.append(DaycareCenter.crspec.like(f"%{special_service}%"))

        # Vector search results filter (if available)
        if vector_stcodes:
            conditions.append(DaycareCenter.stcode.in_(vector_stcodes))

        # Execute query
        query_obj = session.query(DaycareCenter).filter(and_(*conditions))

        # Limit results
        daycares = query_obj.limit(settings.TOP_K).all()

        print(f"   [OK] Database filter: {len(daycares)} results")

        # Convert to dict
        search_results = [daycare.to_dict() for daycare in daycares]

        session.close()

        return {
            **state,
            "search_results": search_results,
            "metadata": {
                **state.get("metadata", {}),
                "total_results": len(search_results),
                "filters_applied": list(filters.keys()),
            },
        }

    except Exception as e:
        print(f"[ERROR] Retriever error: {e}")
        return {
            **state,
            "search_results": [],
            "metadata": {
                **state.get("metadata", {}),
                "retriever_error": str(e),
            },
        }
