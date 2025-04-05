import faiss
import numpy as np
import json

def load_faiss_index(index_path, metadata_path):
    """Charge l'index FAISS et ses métadonnées."""
    index = faiss.read_index(index_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

def search_in_faiss(index, question_embedding, k=5):
    """Effectue une recherche dans l'index FAISS."""
    question_embedding_np = np.array([question_embedding])
    distances, indices = index.search(question_embedding_np, k)
    return distances, indices
