"""
Semantic Similarity Scorer — sentence-transformers cosine similarity.
Detects analogous skill pairs (e.g., Kafka ↔ Kinesis).
Cheap, local computation using all-MiniLM-L6-v2.
"""

# TODO: Implement in Phase 5
# - Load sentence-transformers model (cached)
# - Encode resume + JD skills as embeddings
# - Pairwise cosine similarity matrix
# - Analogous pair detection above threshold
# - Build analogous_pairs[] output
