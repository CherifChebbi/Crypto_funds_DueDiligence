import json
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# === Configuration générale ===
MODEL_NAME = "nomic-ai/nomic-embed-text-v1"
OUTPUT_DIR = Path("output")
EMBEDDING_DIM = 768

# === Chargement du modèle ===
print("🔄 Chargement du modèle d'embedding...")
model = SentenceTransformer(MODEL_NAME)
print(f"✅ Modèle chargé : {MODEL_NAME}")

# === Initialisation de FAISS ===
index = faiss.IndexFlatL2(EMBEDDING_DIM)
metadata = []

# === Traitement de chaque document ===
doc_folders = list(OUTPUT_DIR.iterdir())
print(f"\n📁 {len(doc_folders)} documents à traiter...\n")

for doc_folder in tqdm(doc_folders, desc="📚 Embedding des documents"):
    chunk_path = doc_folder / "cleaned_chunks.jsonl"
    
    if not chunk_path.exists():
        print(f"⚠️  Ignoré : {doc_folder.name} → Aucun 'cleaned_chunks.jsonl' trouvé.")
        continue

    print(f"\n📄 Traitement : {doc_folder.name}")
    
    with open(chunk_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            chunk_text = data["text"]
            chunk_id = data["chunk_id"]

            embedding = model.encode(chunk_text)
            embedding_np = np.array([embedding])

            index.add(embedding_np)
            metadata.append({
                "doc_name": doc_folder.name,
                "chunk_id": chunk_id,
                "text": chunk_text[:100]
            })

# === Sauvegardes ===
print(f"\n✅ Embedding terminé. Total de vecteurs embarqués : {index.ntotal}")

faiss.write_index(index, "faiss_index.bin")
print("💾 Index FAISS sauvegardé → faiss_index.bin")

with open("faiss_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
print("💾 Métadonnées sauvegardées → faiss_metadata.json")

print("\n🎉 Tous les documents ont été indexés avec succès !")
