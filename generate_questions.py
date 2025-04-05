import json
from pathlib import Path
import ollama
from tqdm import tqdm
import time

# === Config ===
MODEL_NAME = "llama2"  # ou "mistral"
OUTPUT_DIR = Path("output")

# === Fonction de génération de questions ===
def generate_questions_from_chunk(chunk_text):
    prompt = f"""Voici un extrait de document lié aux actifs numériques :

\"\"\"{chunk_text}\"\"\"

Génère 3 questions précises portant sur :
1. La stratégie d’investissement
2. Les risques
3. Les aspects réglementaires

Utilise un format clair et structuré.
"""
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {"role": "user", "content": prompt}
        ])
        return response["message"]["content"]
    except Exception as e:
        print("❌ Erreur lors de la requête Ollama :", e)
        return ""

# === Pipeline complet ===
def process_chunks_and_generate_questions():
    print("🚀 Démarrage de la génération des questions...\n")

    for folder in sorted(OUTPUT_DIR.iterdir()):
        if not folder.is_dir():
            continue

        jsonl_path = folder / "cleaned_chunks.jsonl"
        if not jsonl_path.exists():
            print(f"⚠️ {folder.name} : Aucun cleaned_chunks.jsonl trouvé, ignoré.")
            continue

        print(f"\n📄 Document : {folder.name}")
        print("=" * 40)

        # Lecture des chunks
        with open(jsonl_path, "r", encoding="utf-8") as f:
            chunks = [json.loads(line)["text"] for line in f]

        questions = []

        for idx, chunk in enumerate(tqdm(chunks, desc=f"💬 Traitement des chunks ({folder.name})")):
            output = generate_questions_from_chunk(chunk)
            if not output.strip():
                continue
            for q in output.strip().split("\n"):
                cleaned_q = q.strip("-•1234567890. ").strip()
                if cleaned_q:
                    questions.append({
                        "question": cleaned_q,
                        "source": folder.name,
                        "chunk_id": f"{folder.name}_chunk_{idx+1}"
                    })
            time.sleep(0.3)  # Pause pour éviter surcharge Ollama

        # Sauvegarde
        questions_jsonl_path = folder / "questions.jsonl"
        with open(questions_jsonl_path, "w", encoding="utf-8") as f:
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + "\n")

        print(f"✅ {len(questions)} questions générées → {questions_jsonl_path}")

    print("\n🎯 Génération terminée pour tous les documents.")

# === Lancement principal ===
if __name__ == "__main__":
    process_chunks_and_generate_questions()
