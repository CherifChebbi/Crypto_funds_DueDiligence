import os
import json
from tqdm import tqdm
import ollama
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from huggingface_hub import login
import requests
from bs4 import BeautifulSoup

# === Load Hugging Face Token from .env ===
load_dotenv()  # Load environment variables from .env file
huggingface_token = os.getenv("huggingface_token")

if huggingface_token is None:
    print("💥 Hugging Face token not found in .env file!")
else:
    print("✅ Hugging Face token loaded successfully.")
    # Authenticate with Hugging Face
    login(token=huggingface_token)

# === Configuration ===
MODEL_NAME = "llama2"  # Or "mistral" based on your choice
FAISS_INDEX_PATH = "faiss_index.bin"
FAISS_METADATA_PATH = "faiss_metadata.json"
SIMILARITY_THRESHOLD = 0.5  # Similarity threshold for triggering web search
WEB_SEARCH_TRIGGER = True  # Set to True to enable web search
OUTPUT_DIR = "output"  # Directory for storing outputs

# === Load the embedding model for search ===
embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

# Load the FAISS index
try:
    index = faiss.read_index(FAISS_INDEX_PATH)
    print("✅ FAISS index loaded successfully.")
except Exception as e:
    print(f"💥 Error loading FAISS index: {e}")

# Load the associated metadata
try:
    with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print("✅ FAISS metadata loaded successfully.")
except Exception as e:
    print(f"💥 Error loading metadata: {e}")

# Function to retrieve the embedding of a question
def get_question_embedding(question):
    return embedding_model.encode(question)

# Function to search in FAISS
def search_in_faiss(question_embedding):
    question_embedding_np = np.array([question_embedding])
    distances, indices = index.search(question_embedding_np, k=5)  # Top 5 results
    return distances, indices

# Function to perform a web search
def perform_web_search(query):
    search_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    # Perform the search using requests and BeautifulSoup to parse results
    response = requests.get(search_url, headers=headers)
    
    # If request is successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract first few links from the search result
        links = [a['href'] for a in soup.find_all('a', href=True)][:5]  # Get the top 5 links
        return links
    else:
        print(f"💥 Web search failed with status code {response.status_code}")
        return []

# Function to generate an answer using RAG
def generate_answer_with_rag(question):
    question_embedding = get_question_embedding(question)

    # Recherche dans FAISS
    distances, indices = search_in_faiss(question_embedding)

    # Vérifier la pertinence des résultats
    if np.min(distances) < SIMILARITY_THRESHOLD:
        print(f"💡 Similarity threshold not met, triggering web search...")
        if WEB_SEARCH_TRIGGER:
            web_links = perform_web_search(question)
            if web_links:
                return f"🔍 Web search triggered. Here are some links that might help: {', '.join(web_links)}"
        return "Sorry, I couldn't find enough information in the documents."

    # Sinon, générer une réponse à partir des documents les plus pertinents
    relevant_texts = [metadata[i]["text"] for i in indices[0]]
    context = " ".join(relevant_texts)
    prompt = f"Here is some useful information to answer the question:\n{context}\n\nAnswer this question: {question}"

    response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
    
    # Validation de la réponse
    answer = response["message"]["content"]
    if len(answer.split()) < 10:  # Si la réponse est trop courte, la recherche web est déclenchée
        print("💥 Generated answer is too short, triggering web search...")
        web_links = perform_web_search(question)
        if web_links:
            return f"🔍 Web search triggered. Here are some links that might help: {', '.join(web_links)}"
    
    return answer


# Main function to process questions and generate answers
def process_questions_and_generate_answers():
    answers = []
    
    # Itérer à travers tous les sous-dossiers du répertoire OUTPUT_DIR
    for folder in os.listdir(OUTPUT_DIR):
        folder_path = os.path.join(OUTPUT_DIR, folder)

        if os.path.isdir(folder_path):
            try:
                ranked_jsonl_path = os.path.join(folder_path, "ranked_questions.jsonl")
                cleaned_chunks_jsonl_path = os.path.join(folder_path, "cleaned_chunks.jsonl")

                if os.path.exists(ranked_jsonl_path) and os.path.exists(cleaned_chunks_jsonl_path):
                    print(f"🔄 Processing questions in {ranked_jsonl_path}...")
                    
                    with open(ranked_jsonl_path, "r", encoding="utf-8") as f:
                        ranked_questions = [json.loads(line) for line in f]
                    
                    with open(cleaned_chunks_jsonl_path, "r", encoding="utf-8") as f:
                        cleaned_chunks = [json.loads(line) for line in f]
                    
                    # Process each question
                    for question_data in ranked_questions:
                        question_text = question_data["question"]
                        answer = generate_answer_with_rag(question_text)
                        answers.append({
                            "question": question_text,
                            "answer": answer,
                            "source": question_data["source"],
                            "chunk_id": question_data["chunk_id"]
                        })

                    # Save the answers to a file in the same subfolder
                    answers_file = os.path.join(folder_path, "generated_answers.jsonl")
                    with open(answers_file, "w", encoding="utf-8") as f:
                        for answer in answers:
                            f.write(json.dumps(answer, ensure_ascii=False) + "\n")
                    
                    print(f"✅ Answers generated and saved in {answers_file}")
                else:
                    print(f"💥 Missing necessary files in {folder_path}. Skipping this folder.")
            except Exception as e:
                print(f"💥 Error processing folder {folder}: {e}")

if __name__ == "__main__":
    process_questions_and_generate_answers()
