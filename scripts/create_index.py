"""
FAISS Vector Index Creation Script
Creates FAISS index from daycare center embeddings
"""

import json
import sys
from pathlib import Path
import numpy as np
import faiss

# Add app directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

from database import get_session, DaycareCenter
from services import EmbeddingService
from config import settings


def load_daycare_data():
    """Load daycare centers from database"""
    print("📂 Loading daycare centers from database...")

    session = get_session()
    daycares = session.query(DaycareCenter).filter(
        DaycareCenter.crstatusname == "정상"  # Only active daycares
    ).all()

    print(f"✅ Loaded {len(daycares)} daycare centers")
    session.close()

    return daycares


def generate_embeddings(daycares: list, embedding_service: EmbeddingService):
    """Generate embeddings for all daycare centers"""
    print("\n🔄 Generating embeddings...")

    # Extract embedding texts
    texts = []
    stcodes = []

    for daycare in daycares:
        embedding_text = daycare.get_embedding_text()
        if embedding_text:
            texts.append(embedding_text)
            stcodes.append(daycare.stcode)

    print(f"   - Total texts to embed: {len(texts)}")

    # Generate embeddings in batches
    embeddings = embedding_service.embed_batch(texts)

    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   - Embedding shape: {embeddings.shape}")

    return embeddings, stcodes


def create_faiss_index(embeddings: np.ndarray):
    """Create FAISS index from embeddings"""
    print("\n🔧 Creating FAISS index...")

    dimension = embeddings.shape[1]
    num_vectors = embeddings.shape[0]

    print(f"   - Dimension: {dimension}")
    print(f"   - Number of vectors: {num_vectors}")

    # Use IndexFlatL2 for exact search (accuracy priority)
    index = faiss.IndexFlatL2(dimension)

    # Add vectors to index
    index.add(embeddings)

    print(f"✅ FAISS index created")
    print(f"   - Index type: IndexFlatL2")
    print(f"   - Total vectors: {index.ntotal}")

    return index


def save_index(index, stcodes: list):
    """Save FAISS index and metadata"""
    print("\n💾 Saving FAISS index and metadata...")

    # Ensure directory exists
    settings.VECTOR_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # Save FAISS index
    index_path = settings.get_vector_index_path()
    faiss.write_index(index, str(index_path))
    print(f"   ✓ Index saved to: {index_path}")

    # Save metadata (stcode mapping)
    metadata = {
        "stcodes": stcodes,
        "dimension": index.d,
        "total_vectors": index.ntotal,
        "index_type": "IndexFlatL2",
    }

    metadata_path = settings.get_vector_metadata_path()
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"   ✓ Metadata saved to: {metadata_path}")

    print(f"✅ Index and metadata saved successfully")


def verify_index():
    """Verify the created index"""
    print("\n🔍 Verifying index...")

    # Load index
    index_path = settings.get_vector_index_path()
    index = faiss.read_index(str(index_path))

    # Load metadata
    metadata_path = settings.get_vector_metadata_path()
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"✅ Index verification:")
    print(f"   - Total vectors: {index.ntotal}")
    print(f"   - Dimension: {index.d}")
    print(f"   - Metadata entries: {len(metadata['stcodes'])}")
    print(f"   - Index type: {metadata['index_type']}")

    # Test search
    print("\n🔍 Testing search...")
    embedding_service = EmbeddingService()
    test_query = "강남구 국공립 어린이집"
    query_embedding = embedding_service.embed_text(test_query)
    query_embedding = np.array([query_embedding])

    k = 5
    distances, indices = index.search(query_embedding, k)

    print(f"   Query: '{test_query}'")
    print(f"   Top {k} results:")
    for i, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
        stcode = metadata["stcodes"][idx]
        print(f"      {i}. stcode={stcode}, distance={dist:.4f}")

    print(f"✅ Search test successful")


def main():
    """Main workflow"""
    print("=" * 60)
    print("FAISS Vector Index Creation")
    print("=" * 60)

    # Check if database exists
    db_path = settings.get_db_path()
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("   Please run 'python scripts/preprocess_data.py' first")
        return

    # Initialize embedding service
    print("\n1️⃣  Initializing embedding service...")
    try:
        embedding_service = EmbeddingService()
        print("✅ Embedding service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize embedding service: {e}")
        print("   Please check your .env file and Azure OpenAI configuration")
        return

    # Load data
    print("\n2️⃣  Loading daycare data...")
    daycares = load_daycare_data()

    if not daycares:
        print("❌ No daycare centers found in database")
        return

    # Generate embeddings
    print("\n3️⃣  Generating embeddings...")
    embeddings, stcodes = generate_embeddings(daycares, embedding_service)

    # Create FAISS index
    print("\n4️⃣  Creating FAISS index...")
    index = create_faiss_index(embeddings)

    # Save index and metadata
    print("\n5️⃣  Saving index and metadata...")
    save_index(index, stcodes)

    # Verify
    print("\n6️⃣  Verifying index...")
    verify_index()

    print("\n" + "=" * 60)
    print("✅ FAISS index creation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
