import pdfplumber
from pathlib import Path
import os
import requests

# Configuration
PDF_DIR = Path("user_documents")  # Répertoire des documents téléchargés par l'utilisateur
EDGAR_BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
CMC_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"
ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"

# Fonction pour extraire le texte d'un fichier PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Fonction pour traiter les documents de l'utilisateur
def process_user_documents(pdf_file):
    text = extract_text_from_pdf(pdf_file)
    fund_name = extract_fund_name(text)
    edgar_data = search_edgar(fund_name)
    return fund_name, edgar_data

# Extraction du nom du fonds depuis le texte
def extract_fund_name(text):
    fund_name = None
    for line in text.split("\n"):
        if "Fund Name" in line:
            fund_name = line.split(":")[-1].strip()
            break
    return fund_name if fund_name else "Nom du fonds inconnu"

# Recherche EDGAR
def search_edgar(fund_name):
    url = f"{EDGAR_BASE_URL}?action=getcompany&CIK={fund_name}&type=10-K"
    response = requests.get(url)
    return response.text
