"""
FAISS Vector Store Service
Handles vector similarity search for daycare centers
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import faiss

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings
from services.embeddings import EmbeddingService


class VectorStoreService:
    """Service for FAISS vector similarity search"""

    def __init__(self):
        """Initialize vector store and load FAISS index"""
        self.embedding_service = EmbeddingService()
        self.index: Optional[faiss.Index] = None
        self.metadata: Optional[dict] = None
        self.stcodes: Optional[List[str]] = None

        # Try to load existing index
        self.load_index()

    def load_index(self):
        """Load FAISS index and metadata from disk"""
        index_path = settings.get_vector_index_path()
        metadata_path = settings.get_vector_metadata_path()

        if not index_path.exists():
            print(f"[WARN]  FAISS index not found at: {index_path}")
            print("   Please run 'python scripts/create_index.py' first")
            return False

        if not metadata_path.exists():
            print(f"[WARN]  Metadata not found at: {metadata_path}")
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))

            # Load metadata
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
                self.stcodes = self.metadata["stcodes"]

            print(f"[OK] Vector store loaded:")
            print(f"   - Total vectors: {self.index.ntotal}")
            print(f"   - Dimension: {self.index.d}")

            return True

        except Exception as e:
            print(f"[ERROR] Failed to load vector store: {e}")
            return False

    def search(
        self, query: str, top_k: int = None, threshold: float = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar daycare centers

        Args:
            query: Search query text
            top_k: Number of results to return (default from settings)
            threshold: Similarity threshold (default from settings)

        Returns:
            List of (stcode, distance) tuples
        """
        if self.index is None:
            print("[WARN]  Vector store not loaded")
            return []

        if top_k is None:
            top_k = settings.TOP_K

        if threshold is None:
            threshold = settings.SIMILARITY_THRESHOLD

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)
            query_embedding = np.array([query_embedding])  # Shape: (1, dimension)

            # Search
            distances, indices = self.index.search(query_embedding, top_k)

            # Filter by threshold and return results
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                # Convert L2 distance to similarity score (lower is better)
                # For filtering, we can use a distance threshold
                if idx < len(self.stcodes):
                    stcode = self.stcodes[idx]
                    results.append((stcode, float(dist)))

            return results

        except Exception as e:
            print(f"[ERROR] Search error: {e}")
            return []

    def search_batch(
        self, queries: List[str], top_k: int = None
    ) -> List[List[Tuple[str, float]]]:
        """
        Search for multiple queries

        Args:
            queries: List of search query texts
            top_k: Number of results per query

        Returns:
            List of result lists, one per query
        """
        if self.index is None:
            print("[WARN]  Vector store not loaded")
            return [[] for _ in queries]

        if top_k is None:
            top_k = settings.TOP_K

        try:
            # Generate query embeddings
            query_embeddings = self.embedding_service.embed_batch(queries)

            # Search
            distances, indices = self.index.search(query_embeddings, top_k)

            # Process results
            all_results = []
            for query_idx, (query_distances, query_indices) in enumerate(
                zip(distances, indices)
            ):
                query_results = []
                for idx, dist in zip(query_indices, query_distances):
                    if idx < len(self.stcodes):
                        stcode = self.stcodes[idx]
                        query_results.append((stcode, float(dist)))
                all_results.append(query_results)

            return all_results

        except Exception as e:
            print(f"[ERROR] Batch search error: {e}")
            return [[] for _ in queries]

    def get_stats(self) -> dict:
        """Get vector store statistics"""
        if self.index is None:
            return {"loaded": False}

        return {
            "loaded": True,
            "total_vectors": self.index.ntotal,
            "dimension": self.index.d,
            "index_type": self.metadata.get("index_type", "unknown"),
        }


# Global vector store instance
vector_store = None


def get_vector_store() -> VectorStoreService:
    """Get or create global vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStoreService()
    return vector_store


if __name__ == "__main__":
    # Test vector store
    print("Testing VectorStoreService...")

    store = VectorStoreService()

    if store.index is not None:
        # Test search
        test_query = "강남구 국공립 어린이집"
        results = store.search(test_query, top_k=5)

        print(f"\n[SEARCH] Query: '{test_query}'")
        print(f"[RESULTS] Top 5 results:")
        for i, (stcode, distance) in enumerate(results, 1):
            print(f"   {i}. stcode={stcode}, distance={distance:.4f}")

        # Get stats
        stats = store.get_stats()
        print(f"\n[STATS] Vector store stats:")
        for key, value in stats.items():
            print(f"   - {key}: {value}")
