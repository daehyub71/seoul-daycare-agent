"""
OpenAI Embedding Service
Handles text embedding generation using Azure OpenAI
"""

import sys
from pathlib import Path
from typing import List
import numpy as np
from openai import OpenAI, AzureOpenAI

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI or Azure OpenAI"""

    def __init__(self):
        """Initialize OpenAI client (OpenAI or Azure)"""
        # Check if using regular OpenAI or Azure OpenAI
        if settings.OPENAI_API_KEY:
            # Use regular OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_EMBEDDING_MODEL
            self.use_azure = False
        elif settings.AOAI_API_KEY:
            # Use Azure OpenAI
            self.client = AzureOpenAI(
                api_key=settings.AOAI_API_KEY,
                api_version=settings.AOAI_API_VERSION,
                azure_endpoint=settings.AOAI_ENDPOINT,
            )
            self.model = settings.AOAI_EMBEDDING_DEPLOYMENT
            self.use_azure = True
        else:
            raise ValueError("Either OPENAI_API_KEY or AOAI_API_KEY must be set in .env file")

        self.dimension = settings.EMBEDDING_DIMENSION

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Input text to embed

        Returns:
            numpy array of shape (dimension,)
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.dimension)

        try:
            response = self.client.embeddings.create(
                input=text, model=self.model
            )
            embedding = response.data[0].embedding
            return np.array(embedding, dtype=np.float32)

        except Exception as e:
            print(f"[WARN]  Embedding error for text '{text[:50]}...': {e}")
            return np.zeros(self.dimension)

    def embed_batch(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of input texts
            batch_size: Batch size for API calls (default from settings)

        Returns:
            numpy array of shape (len(texts), dimension)
        """
        if batch_size is None:
            batch_size = settings.BATCH_SIZE

        embeddings = []
        total = len(texts)

        print(f"[PROCESSING] Generating embeddings for {total} texts...")

        for i in range(0, total, batch_size):
            batch = texts[i : i + batch_size]
            batch_end = min(i + batch_size, total)

            try:
                # Filter out empty texts
                valid_texts = [t if t and t.strip() else " " for t in batch]

                response = self.client.embeddings.create(
                    input=valid_texts, model=self.model
                )

                batch_embeddings = [
                    np.array(item.embedding, dtype=np.float32)
                    for item in response.data
                ]
                embeddings.extend(batch_embeddings)

                print(f"  [OK] Processed {batch_end}/{total} texts...")

            except Exception as e:
                print(f"  [WARN]  Batch error (items {i}-{batch_end}): {e}")
                # Add zero vectors for failed batch
                embeddings.extend(
                    [np.zeros(self.dimension, dtype=np.float32) for _ in batch]
                )

        return np.array(embeddings, dtype=np.float32)


if __name__ == "__main__":
    # Test embedding service
    print("Testing EmbeddingService...")

    service = EmbeddingService()

    # Test single embedding
    test_text = "자이햇살어린이집 서울특별시 성북구 돌곶이로30길 23 210동 104호 가정 일반"
    embedding = service.embed_text(test_text)
    print(f"[OK] Single embedding shape: {embedding.shape}")
    print(f"   First 5 values: {embedding[:5]}")

    # Test batch embedding
    test_texts = [
        "국공립 어린이집 강남구",
        "가정 어린이집 성북구 놀이터",
        "직장 어린이집 CCTV",
    ]
    batch_embeddings = service.embed_batch(test_texts, batch_size=2)
    print(f"[OK] Batch embeddings shape: {batch_embeddings.shape}")
