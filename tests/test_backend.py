"""
Backend Component Tests
Tests database, vector store, and API without running full server
"""

import sys
from pathlib import Path

# Add app directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

print("=" * 60)
print("Backend Component Tests")
print("=" * 60)

# Test 1: Database Connection
print("\n1️⃣  Testing Database Connection...")
try:
    from database import get_session, DaycareCenter
    from sqlalchemy import func

    session = get_session()
    total = session.query(DaycareCenter).count()
    active = session.query(DaycareCenter).filter(
        DaycareCenter.crstatusname == "정상"
    ).count()

    print(f"   ✅ Database connected")
    print(f"   - Total records: {total:,}")
    print(f"   - Active centers: {active:,}")

    # Sample query
    sample = session.query(DaycareCenter).first()
    print(f"   - Sample: {sample.crname} ({sample.crtypename})")

    session.close()

except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test 2: Configuration
print("\n2️⃣  Testing Configuration...")
try:
    from config import settings

    print(f"   ✅ Config loaded")
    print(f"   - DB Path: {settings.get_db_path()}")
    print(f"   - Vector Index: {settings.get_vector_index_path()}")
    print(f"   - OpenAI Key: {'✓ Set' if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your-openai-api-key-here' else '✗ Not set'}")
    print(f"   - Top K: {settings.TOP_K}")

except Exception as e:
    print(f"   ❌ Config error: {e}")

# Test 3: Vector Store (if available)
print("\n3️⃣  Testing Vector Store...")
try:
    from services import get_vector_store

    vector_store = get_vector_store()
    stats = vector_store.get_stats()

    if stats.get("loaded"):
        print(f"   ✅ Vector store loaded")
        print(f"   - Total vectors: {stats.get('total_vectors', 0):,}")
        print(f"   - Dimension: {stats.get('dimension', 0)}")
    else:
        print(f"   ⚠️  Vector store not available (FAISS index not found)")
        print(f"   - Run 'python scripts/create_index.py' to create index")

except Exception as e:
    print(f"   ❌ Vector store error: {e}")

# Test 4: API Routes
print("\n4️⃣  Testing API Routes Import...")
try:
    from api.routes import router

    route_count = len(router.routes)
    print(f"   ✅ API routes loaded")
    print(f"   - Total routes: {route_count}")

    # List routes
    print(f"   - Endpoints:")
    for route in router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"      {methods:8} {route.path}")

except Exception as e:
    print(f"   ❌ API routes error: {e}")

# Test 5: Database Statistics
print("\n5️⃣  Testing Database Queries...")
try:
    from database import get_session, DaycareCenter
    from sqlalchemy import func

    session = get_session()

    # By district
    print(f"   ✅ Query test: Top 5 districts")
    by_district = (
        session.query(
            DaycareCenter.sigunname, func.count(DaycareCenter.id).label("count")
        )
        .filter(DaycareCenter.crstatusname == "정상")
        .group_by(DaycareCenter.sigunname)
        .order_by(func.count(DaycareCenter.id).desc())
        .limit(5)
        .all()
    )

    for district, count in by_district:
        print(f"      - {district}: {count:,}개")

    session.close()

except Exception as e:
    print(f"   ❌ Query error: {e}")

print("\n" + "=" * 60)
print("✅ Backend Component Tests Complete")
print("=" * 60)
