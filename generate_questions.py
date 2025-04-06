import json
import ollama
import re
import time
from pathlib import Path
from tqdm import tqdm
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F
import logging

# === Config ===
MODEL_NAME = "llama2"  # ou "mistral"
OUTPUT_DIR = Path("output")
BERT_MODEL_NAME = 'bert-base-uncased'
CATEGORY_LIST = [
    "Legal and Regulatory Compliance", "Financial Due Diligence", "Technical Due Diligence",
    "Operational Due Diligence", "Market and Competitive Analysis", "Governance",
    "Risk Assessment", "Community and Ecosystem", "Exit and Liquidity",
    "Environmental, Social, and Governance (ESG) Considerations", "Future Roadmap", "Miscellaneous"
]

# === Configuration du logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Initialisation des modèles ===
model = BertForSequenceClassification.from_pretrained(BERT_MODEL_NAME, num_labels=len(CATEGORY_LIST))
tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_NAME)

# === Fonction de génération de questions ===
def generate_questions_from_chunk(chunk_text):
    prompt = f"""Here is a document excerpt related to digital assets:

\"\"\"{chunk_text}\"\"\" 

Generate 3 specific questions on:
1. Investment strategy
2. Risks
3. Regulatory aspects

Please write the questions in English and ensure they are clear and structured.
"""
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        
        # Vérifier si la réponse est une liste ou une chaîne
        output = response["message"]["content"]
        if isinstance(output, list):
            output = "\n".join(output)  # Convertir en chaîne si c'est une liste
            
        return output
    except Exception as e:
        logger.error(f"Error with Ollama request: {e}")
        return ""



# === Fonction de classification des questions ===
def classify_question(question):
    # Tokenisation et classification avec un modèle BERT plus léger
    inputs = tokenizer(question, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)
    category = CATEGORY_LIST[predictions.item()]
    return category


# === Pipeline complet ===
def process_chunks_and_generate_questions():
    logger.info("🚀 Démarrage de la génération des questions...\n")

    for folder in sorted(OUTPUT_DIR.iterdir()):
        if not folder.is_dir():
            continue

        jsonl_path = folder / "cleaned_chunks.jsonl"
        if not jsonl_path.exists():
            logger.warning(f"{folder.name} : Aucun cleaned_chunks.jsonl trouvé, ignoré.")
            continue

        logger.info(f"\n📄 Document : {folder.name}")
        logger.info("=" * 40)

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
                    question = {
                        "question": cleaned_q,
                        "source": folder.name,
                        "chunk_id": f"{folder.name}_chunk_{idx+1}"
                    }
                    # Classification de la question
                    question['category'] = classify_question(cleaned_q)
                    questions.append(question)
            time.sleep(0.3)  # Pause pour éviter surcharge Ollama

        # Sauvegarde des questions classées
        questions_jsonl_path = folder / "ranked_questions.jsonl"
        with open(questions_jsonl_path, "w", encoding="utf-8") as f:
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + "\n")

        logger.info(f"✅ {len(questions)} questions générées et classées → {questions_jsonl_path}")

    logger.info("\n🎯 Génération terminée pour tous les documents.")

# === Lancement principal ===
if __name__ == "__main__":
    process_chunks_and_generate_questions()
