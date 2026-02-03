#!/usr/bin/env python3
"""Test embedding generation."""

from lib.embedder import get_embedder, serialize_embedding


def main():
    print("Testing Ollama embedder...")
    embedder = get_embedder('nomic-embed-text')
    print(f"Model: {embedder.model_name}")
    print(f"Dimensions: {embedder.dimensions}")

    # Test single embedding
    text = "This is a test sentence about Python programming."
    embedding = embedder.embed_one(text)
    print(f"Single embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test batch embedding
    texts = [
        "First test sentence.",
        "Second test sentence.",
        "Third test sentence."
    ]
    embeddings = embedder.embed(texts)
    print(f"Batch embeddings: {len(embeddings)} vectors")

    # Test serialization
    serialized = serialize_embedding(embedding)
    print(f"Serialized size: {len(serialized)} bytes")

    print("\n✓ Embedder working correctly")


if __name__ == '__main__':
    main()
