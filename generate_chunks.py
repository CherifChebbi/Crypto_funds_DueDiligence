import os
import json
from pathlib import Path

CHUNK_SEPARATOR = "\n\n"
CHUNK_SIZE_WORDS = 120  # taille approximative en mots
OUTPUT_DIR = "output"

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE_WORDS):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def process_all_cleaned_texts():
    for folder in os.listdir(OUTPUT_DIR):
        folder_path = os.path.join(OUTPUT_DIR, folder)
        cleaned_txt_path = os.path.join(folder_path, "cleaned.txt")

        if not os.path.exists(cleaned_txt_path):
            continue

        with open(cleaned_txt_path, "r", encoding="utf-8") as f:
            cleaned_text = f.read()

        chunks = split_text_into_chunks(cleaned_text)

        jsonl_path = os.path.join(folder_path, "cleaned_chunks.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                entry = {
                    "text": chunk.strip(),
                    "source": folder,
                    "chunk_id": f"{folder}_chunk_{i+1}"
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"[✓] {folder} découpé en {len(chunks)} chunks → cleaned_chunks.jsonl")

if __name__ == "__main__":
    process_all_cleaned_texts()
