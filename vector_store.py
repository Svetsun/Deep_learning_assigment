import numpy as np
import polars as pl

class VectorStore:
    def __init__(self):
        self.vectors = []
        self.texts = []
        self.metadata = []

    def add_item(self, text, embedding, metadata=None):
        self.vectors.append(np.array(embedding))
        self.texts.append(text)
        self.metadata.append(metadata or {})

    def semantic_search(self, query_embedding, k=5):
        if not self.vectors:
            return []

        query_vector = np.array(query_embedding)
        similarities = []
        for i, vector in enumerate(self.vectors):
            similarity = np.dot(query_vector, vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(vector) + 1e-10
            )
            similarities.append((i, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)

        results = []
        for i in range(min(k, len(similarities))):
            idx, score = similarities[i]
            results.append({
                "text": self.texts[idx],
                "metadata": self.metadata[idx],
                "similarity": score
            })

        return results

    def save(self, filepath="data/embeddings.parquet"):
        vector_list = [vec.tolist() for vec in self.vectors]
        df = pl.DataFrame(
            {
                "vectors": vector_list,
                "texts": self.texts,
                "metadata": self.metadata
            }
        )
        df.write_parquet(filepath)

    def load(self, filepath):
        df = pl.read_parquet(filepath, columns=["vectors", "texts", "metadata"])
        self.vectors = [np.array(vec) for vec in df["vectors"].to_list()]
        self.texts = df["texts"].to_list()
        self.metadata = df["metadata"].to_list()
