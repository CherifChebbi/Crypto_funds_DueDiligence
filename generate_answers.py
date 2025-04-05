import json
from pathlib import Path
import ollama
import faiss
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# === Configuration ===
MODEL_NAME = "llama2"  # Ou "mistral" selon ton choix
FAISS_INDEX_PATH = "faiss_index.bin"
FAISS_METADATA_PATH = "faiss_metadata.json"
SIMILARITY_THRESHOLD = 0.7  # Seuil de similarité pour déclencher la recherche web
WEB_SEARCH_TRIGGER = False  # Si False, pas de recherche web (peut être activé selon besoin)

# === Chargement du modèle d'embedding pour la recherche ===
embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1")
index = faiss.read_index(FAISS_INDEX_PATH)

# Chargement des métadonnées associées
with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Fonction pour récupérer les embeddings d'une question
def get_question_embedding(question):
    return embedding_model.encode(question)

# Fonction pour rechercher dans FAISS
def search_in_faiss(question_embedding):
    question_embedding_np = np.array([question_embedding])
    distances, indices = index.search(question_embedding_np, k=5)  # 5 meilleurs résultats
    return distances, indices

# Fonction pour générer des réponses avec RAG
def generate_answer_with_rag(question):
    question_embedding = get_question_embedding(question)

    # Recherche dans l'index FAISS
    distances, indices = search_in_faiss(question_embedding)

    # Vérifier si les résultats sont suffisamment proches
    if np.min(distances) < SIMILARITY_THRESHOLD:
        print(f"💡 Similarité insuffisante, activation de la recherche web...")
        # Optionnel : Mettre en place une recherche web si nécessaire
        if WEB_SEARCH_TRIGGER:
            # Code pour récupérer les informations via une recherche web (à ajouter ici)
            pass
        return "Désolé, je n'ai pas trouvé d'informations suffisantes dans les documents."

    # Sinon, générer une réponse avec les documents les plus pertinents
    relevant_texts = [metadata[i]["text"] for i in indices[0]]
    context = " ".join(relevant_texts)
    prompt = f"Voici quelques informations utiles pour répondre à la question :\n{context}\n\nRéponds à cette question : {question}"

    # Appel à Ollama pour générer la réponse
    response = ollama.chat(model=MODEL_NAME, messages=[
        {"role": "user", "content": prompt}
    ])
    
    return response["message"]["content"]

# Fonction principale pour traiter les questions
def process_questions_and_generate_answers():
    question_file = Path("output") / "questions.jsonl"
    answers = []

    with open(question_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="🔄 Traitement des questions", total=sum(1 for _ in f)):
            question_data = json.loads(line)
            question_text = question_data["question"]
            answer = generate_answer_with_rag(question_text)
            answers.append({
                "question": question_text,
                "answer": answer,
                "source": question_data["source"],
                "chunk_id": question_data["chunk_id"]
            })
    
    # Sauvegarde des réponses dans un fichier
    answers_file = Path("output") / "generated_answers.jsonl"
    with open(answers_file, "w", encoding="utf-8") as f:
        for answer in answers:
            f.write(json.dumps(answer, ensure_ascii=False) + "\n")
    
    print(f"✅ Réponses générées et sauvegardées dans {answers_file}")

if __name__ == "__main__":
    process_questions_and_generate_answers()
