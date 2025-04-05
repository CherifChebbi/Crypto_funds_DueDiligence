import streamlit as st
from process_user_documents_and_search import process_user_documents, search_external_info
from search_utils import create_faiss_index, search_faiss

# Créer un index FAISS
index = create_faiss_index()

# Titre de l'application
st.title("Q&A System pour fonds et cryptomonnaies")

# Section de téléchargement de fichiers
uploaded_files = st.file_uploader("Téléchargez vos documents PDF", type="pdf", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Traiter les fichiers PDF et extraire les informations
        st.write(f"Traitement du fichier : {uploaded_file.name}")
        process_user_documents(uploaded_file)

# Section de question
question = st.text_input("Posez votre question")
if question:
    # Recherche interne via FAISS
    result = search_faiss(index, question)
    st.write(f"Résultats internes : {result}")
    
    # Recherche externe via les APIs
    search_external_info(question)
