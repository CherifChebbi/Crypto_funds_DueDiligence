import faiss
import numpy as np
import json

# Chargement de l'index FAISS et des métadonnées
def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

# Recherche dans FAISS
def search_in_faiss(index, question_embedding, k=5):
    question_embedding_np = np.array([question_embedding])
    distances, indices = index.search(question_embedding_np, k)
    return distances, indices
