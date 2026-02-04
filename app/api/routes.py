"""
FastAPI Routes
API endpoints for daycare search service
"""

import sys
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_session, DaycareCenter
from workflows.graph_builder import run_search_workflow_sync
from sqlalchemy import func

router = APIRouter()


# Request/Response Models
class SearchRequest(BaseModel):
    """Search request model"""

    query: str = Field(..., description="User search query", min_length=1)
    filters: Optional[dict] = Field(default={}, description="Additional filters")


class SearchResponse(BaseModel):
    """Search response model"""

    query: str
    answer: str
    results: List[dict]
    total: int
    metadata: dict


class DaycareDetail(BaseModel):
    """Daycare center detail model"""

    stcode: str
    crname: str
    crtypename: Optional[str] = None
    crstatusname: Optional[str] = None
    craddr: Optional[str] = None
    sigunname: Optional[str] = None
    la: Optional[float] = None
    lo: Optional[float] = None
    crtelno: Optional[str] = None
    crcapat: Optional[int] = None
    crchcnt: Optional[int] = None
    plgrdco: Optional[int] = None
    cctvinstlcnt: Optional[int] = None


@router.post("/search", response_model=SearchResponse)
async def search_daycares(request: SearchRequest):
    """
    Search for daycare centers using AI workflow

    Args:
        request: Search request with query and optional filters

    Returns:
        Search results with AI-generated answer
    """
    try:
        # Run LangGraph workflow
        result = run_search_workflow_sync(request.query)

        return SearchResponse(
            query=request.query,
            answer=result.get("answer", ""),
            results=result.get("search_results", []),
            total=len(result.get("search_results", [])),
            metadata=result.get("metadata", {}),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/daycares/{stcode}", response_model=DaycareDetail)
async def get_daycare_detail(stcode: str):
    """
    Get detailed information for a specific daycare center

    Args:
        stcode: Daycare center code

    Returns:
        Detailed daycare center information
    """
    session = get_session()

    try:
        daycare = (
            session.query(DaycareCenter)
            .filter(DaycareCenter.stcode == stcode)
            .first()
        )

        if not daycare:
            raise HTTPException(status_code=404, detail="Daycare center not found")

        result = daycare.to_dict()
        session.close()

        return DaycareDetail(**result)

    except HTTPException:
        raise
    except Exception as e:
        session.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/districts")
async def get_districts():
    """
    Get list of all districts (시군구)

    Returns:
        List of district names with counts
    """
    session = get_session()

    try:
        districts = (
            session.query(
                DaycareCenter.sigunname, func.count(DaycareCenter.id).label("count")
            )
            .filter(DaycareCenter.crstatusname == "정상")
            .group_by(DaycareCenter.sigunname)
            .order_by(func.count(DaycareCenter.id).desc())
            .all()
        )

        result = [{"name": d[0], "count": d[1]} for d in districts if d[0]]

        session.close()
        return {"districts": result, "total": len(result)}

    except Exception as e:
        session.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/types")
async def get_types():
    """
    Get list of all daycare types

    Returns:
        List of daycare types with counts
    """
    session = get_session()

    try:
        types = (
            session.query(
                DaycareCenter.crtypename, func.count(DaycareCenter.id).label("count")
            )
            .filter(DaycareCenter.crstatusname == "정상")
            .group_by(DaycareCenter.crtypename)
            .order_by(func.count(DaycareCenter.id).desc())
            .all()
        )

        result = [{"name": t[0], "count": t[1]} for t in types if t[0]]

        session.close()
        return {"types": result, "total": len(result)}

    except Exception as e:
        session.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/compare")
async def compare_daycares(stcodes: List[str] = Query(..., description="Daycare codes to compare")):
    """
    Compare multiple daycare centers

    Args:
        stcodes: List of daycare center codes

    Returns:
        Comparison table data
    """
    session = get_session()

    try:
        daycares = (
            session.query(DaycareCenter)
            .filter(DaycareCenter.stcode.in_(stcodes))
            .all()
        )

        if not daycares:
            raise HTTPException(status_code=404, detail="No daycare centers found")

        results = [d.to_dict() for d in daycares]
        session.close()

        return {"daycares": results, "total": len(results)}

    except HTTPException:
        raise
    except Exception as e:
        session.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/stats")
async def get_statistics():
    """
    Get overall statistics

    Returns:
        Database statistics
    """
    session = get_session()

    try:
        total = session.query(DaycareCenter).filter(
            DaycareCenter.crstatusname == "정상"
        ).count()

        # By district
        by_district = (
            session.query(
                DaycareCenter.sigunname, func.count(DaycareCenter.id).label("count")
            )
            .filter(DaycareCenter.crstatusname == "정상")
            .group_by(DaycareCenter.sigunname)
            .order_by(func.count(DaycareCenter.id).desc())
            .limit(10)
            .all()
        )

        # By type
        by_type = (
            session.query(
                DaycareCenter.crtypename, func.count(DaycareCenter.id).label("count")
            )
            .filter(DaycareCenter.crstatusname == "정상")
            .group_by(DaycareCenter.crtypename)
            .order_by(func.count(DaycareCenter.id).desc())
            .all()
        )

        session.close()

        return {
            "total": total,
            "by_district": [{"name": d[0], "count": d[1]} for d in by_district],
            "by_type": [{"name": t[0], "count": t[1]} for t in by_type],
        }

    except Exception as e:
        session.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
