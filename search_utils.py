import faiss
import numpy as np
from transformers import BertTokenizer, BertModel

# Chargement du modèle BERT pour la génération d'embeddings
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Fonction pour générer des embeddings à partir du texte
def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

# Index FAISS pour stocker les embeddings
def create_faiss_index():
    # Exemple d'embeddings pour l'index FAISS
    embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])  # Remplace par tes embeddings
    index = faiss.IndexFlatL2(3)  # 3 correspond à la dimension des embeddings
    index.add(embeddings)
    return index

# Fonction pour rechercher une question dans FAISS
def search_faiss(index, question):
    question_embedding = generate_embedding(question)
    D, I = index.search(question_embedding, 5)  # Cherche les 5 plus proches voisins
    return I  # Retourne les indices des documents les plus similaires
