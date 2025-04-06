import streamlit as st
from process_user_documents_and_search import process_user_documents, search_external_info
from search_utils import create_faiss_index, search_faiss
from langchain_utils import generate_answer_with_llama
from create_report import create_report
from generate_performance_graph import generate_performance_chart
from qna_data_extraction import extract_fund_insights

# Créer un index FAISS pour la recherche interne
index = create_faiss_index()

# Titre de l'application
st.title("Système Q&A pour Fonds et Cryptomonnaies")

# Section de téléchargement de fichiers
st.subheader("Téléchargez vos documents PDF pour traitement")
uploaded_files = st.file_uploader("Téléchargez vos fichiers PDF", type="pdf", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Traiter chaque fichier PDF et extraire les informations pertinentes
        st.write(f"Traitement du fichier : {uploaded_file.name}")
        process_user_documents(uploaded_file)  # Traitement des documents PDF

# Section de question
st.subheader("Posez une question sur les fonds ou les cryptomonnaies")
question = st.text_input("Entrez votre question ici")
if question:
    # Recherche interne dans les documents via FAISS
    result = search_faiss(index, question)
    st.write(f"Résultats internes : {result}")
    
    # Recherche externe via les APIs (ex. EDGAR, autres bases de données)
    external_info = search_external_info(question)
    st.write(f"Résultats externes : {external_info}")
    
    # Combiner les résultats internes et externes et générer une réponse via LLaMA
    answer = generate_answer_with_llama(result, external_info, question)
    st.write(f"Réponse générée : {answer}")

    # Extrait les informations clés pour la génération du rapport
    fund_data = {
        "performance": "15% de retour sur investissement sur 1 an",  # Exemples fictifs
        "compliance": "Conforme à la réglementation AIFMD",
        "asset_size": 500000000,
        "risk_score": 7,
        "latest_report_date": "2025-03-30"
    }
    insights = extract_fund_insights(fund_data)

    # Génération du graphique de performance
    chart_path = generate_performance_chart([
        {"date": "2024-01-01", "performance": 5},
        {"date": "2024-06-01", "performance": 7},
        {"date": "2025-01-01", "performance": 15}
    ])

    # Générer le rapport PowerPoint
    st.subheader("Générer et télécharger le rapport")
    create_report(insights, chart_path)  # Création du rapport PowerPoint

    # Fournir le lien pour télécharger le rapport généré
    with open("rapport_fonds.pptx", "rb") as f:
        st.download_button(
            label="Téléchargez votre rapport PowerPoint",
            data=f,
            file_name="rapport_fonds.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
