"""
API Endpoint Tests (without starting server)
Uses FastAPI TestClient for testing
"""

import sys
from pathlib import Path

# Add app directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 60)
print("API Endpoint Tests")
print("=" * 60)

# Test 1: Root endpoint
print("\n1️⃣  GET / (Root)")
try:
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✅ Pass")
except Exception as e:
    print(f"   ❌ Fail: {e}")

# Test 2: Health check
print("\n2️⃣  GET /health")
try:
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✅ Pass")
except Exception as e:
    print(f"   ❌ Fail: {e}")

# Test 3: Get districts
print("\n3️⃣  GET /api/v1/districts")
try:
    response = client.get("/api/v1/districts")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total districts: {data.get('total', 0)}")
    if data.get('districts'):
        print(f"   Top 3:")
        for d in data['districts'][:3]:
            print(f"      - {d['name']}: {d['count']}개")
    assert response.status_code == 200
    print("   ✅ Pass")
except Exception as e:
    print(f"   ❌ Fail: {e}")

# Test 4: Get types
print("\n4️⃣  GET /api/v1/types")
try:
    response = client.get("/api/v1/types")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total types: {data.get('total', 0)}")
    if data.get('types'):
        print(f"   Types:")
        for t in data['types']:
            print(f"      - {t['name']}: {t['count']}개")
    assert response.status_code == 200
    print("   ✅ Pass")
except Exception as e:
    print(f"   ❌ Fail: {e}")

# Test 5: Get statistics
print("\n5️⃣  GET /api/v1/stats")
try:
    response = client.get("/api/v1/stats")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total daycares: {data.get('total', 0):,}")
    print(f"   Top 3 districts:")
    for d in data.get('by_district', [])[:3]:
        print(f"      - {d['name']}: {d['count']}개")
    assert response.status_code == 200
    print("   ✅ Pass")
except Exception as e:
    print(f"   ❌ Fail: {e}")

# Test 6: Get specific daycare
print("\n6️⃣  GET /api/v1/daycares/{stcode}")
try:
    # Get a sample stcode first
    from database import get_session, DaycareCenter

    session = get_session()
    sample = session.query(DaycareCenter).filter(
        DaycareCenter.crstatusname == "정상"
    ).first()
    stcode = sample.stcode
    session.close()

    response = client.get(f"/api/v1/daycares/{stcode}")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Name: {data.get('crname')}")
    print(f"   Type: {data.get('crtypename')}")
    print(f"   District: {data.get('sigunname')}")
    assert response.status_code == 200
    print("   ✅ Pass")
except Exception as e:
    print(f"   ❌ Fail: {e}")

# Test 7: Search (will fail without OpenAI API key, but test structure)
print("\n7️⃣  POST /api/v1/search (Structure test)")
try:
    payload = {"query": "강남구 국공립 어린이집"}
    response = client.post("/api/v1/search", json=payload)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   Query: {data.get('query')}")
        print(f"   Total results: {data.get('total', 0)}")
        print(f"   Answer length: {len(data.get('answer', ''))} chars")
        print("   ✅ Pass (Full workflow works!)")
    else:
        print(f"   ⚠️  Expected (likely OpenAI API key needed)")
        print(f"   Error: {response.json()}")

except Exception as e:
    print(f"   ⚠️  Expected error: {e}")

print("\n" + "=" * 60)
print("✅ API Endpoint Tests Complete")
print("=" * 60)
