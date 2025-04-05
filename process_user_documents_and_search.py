import pdfplumber
from pathlib import Path
import os
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# === Configuration ===
OUTPUT_DIR = Path("output")
PDF_DIR = Path("user_documents")  # Répertoire des documents téléchargés par l'utilisateur
EDGAR_BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
CMC_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"
CRUNCHBASE_API_URL = "https://api.crunchbase.com/v3.1/organizations"
ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
FT_API_URL = "https://api.ft.com/content/search/v1"

# --- API Keys (chargées depuis le fichier .env) ---
CMC_API_KEY = os.getenv("CMC_API_KEY")
CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FRED_API_KEY = os.getenv("FRED_API_KEY")
FT_API_KEY = os.getenv("FT_API_KEY")

# === Fonction pour extraire le texte d'un fichier PDF ===
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# === Fonction pour valider le nom du fonds ===
def validate_fund_name(fund_name):
    if not fund_name or len(fund_name.strip()) == 0:
        print("⚠️ Erreur : Le nom du fonds est vide ou mal formaté.")
        return False
    return True

# === Fonction pour valider le CIK ===
def validate_cik(cik):
    if cik.isdigit() and len(cik) == 10:  # Un CIK valide est un identifiant à 10 chiffres
        return True
    else:
        print(f"⚠️ Erreur : CIK invalide : {cik}")
        return False

# === Fonction pour traiter les documents de l'utilisateur (comme des factures, contrats, etc.) ===
def process_user_documents():
    for pdf_file in PDF_DIR.glob("*.pdf"):
        print(f"📄 Traitement du fichier : {pdf_file.name}")

        # Extraire le texte du PDF
        text = extract_text_from_pdf(pdf_file)

        # Extraction d'informations spécifiques (par exemple, le nom du fonds)
        fund_name = extract_fund_name(text)
        if not validate_fund_name(fund_name):
            continue  # Si la validation échoue, passer au fichier suivant
        print(f"📌 Nom du fonds extrait : {fund_name}")

        # Recherche externe d'informations (par exemple via EDGAR)
        edgar_data = search_edgar(fund_name)
        print(f"🔍 Résultats de la recherche EDGAR :\n{edgar_data}")

# === Fonction d'extraction du nom du fonds depuis le texte (exemple simple) ===
def extract_fund_name(text):
    # Implémenter une logique plus sophistiquée d'extraction du nom du fonds
    # Pour l'exemple, supposons qu'on cherche un mot clé comme "Fund Name"
    fund_name = None
    for line in text.split("\n"):
        if "Fund Name" in line:
            fund_name = line.split(":")[-1].strip()
            break
    return fund_name if fund_name else "Nom du fonds inconnu"

# === Recherche EDGAR ===
def search_edgar(fund_name_or_cik, document_type="10-K"):
    if not validate_cik(fund_name_or_cik):  # Valider le CIK avant la recherche
        return f"Recherche EDGAR échouée : CIK invalide."
    
    url = f"{EDGAR_BASE_URL}?action=getcompany&CIK={fund_name_or_cik}&type={document_type}&owner=exclude&count=10"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Erreur EDGAR pour le CIK {fund_name_or_cik}."

# === Recherche CoinMarketCap ===
def search_coinmarketcap(fund_name):
    if not validate_fund_name(fund_name):  # Valider le nom du fonds avant la recherche
        return f"Erreur CoinMarketCap : Nom du fonds invalide."
    
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    params = {'symbol': fund_name}
    response = requests.get(CMC_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Erreur CoinMarketCap pour {fund_name}."

# === Recherche Crunchbase ===
def search_crunchbase(fund_name):
    if not validate_fund_name(fund_name):  # Valider le nom du fonds avant la recherche
        return f"Erreur Crunchbase : Nom du fonds invalide."
    
    params = {'user_key': CRUNCHBASE_API_KEY, 'query': fund_name}
    response = requests.get(CRUNCHBASE_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Erreur Crunchbase pour {fund_name}."

# === Recherche Alpha Vantage ===
def search_alpha_vantage(symbol):
    if not validate_fund_name(symbol):  # Valider le symbole avant la recherche
        return f"Erreur Alpha Vantage : Symbole invalide."
    
    params = {'function': 'TIME_SERIES_DAILY', 'symbol': symbol, 'apikey': ALPHA_VANTAGE_API_KEY}
    response = requests.get(ALPHA_VANTAGE_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Erreur Alpha Vantage pour {symbol}."

# === Recherche FRED ===
def search_fred(series_id):
    if not validate_fund_name(series_id):  # Valider l'ID de série avant la recherche
        return f"Erreur FRED : ID de série invalide."
    
    params = {'series_id': series_id, 'api_key': FRED_API_KEY}
    response = requests.get(FRED_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Erreur FRED pour {series_id}."

# === Recherche FT ===
def search_ft(query):
    if not validate_fund_name(query):  # Valider la requête avant la recherche
        return f"Erreur FT : Requête invalide."
    
    headers = {'Authorization': f'Bearer {FT_API_KEY}'}
    params = {'query': query}
    response = requests.get(FT_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Erreur FT pour {query}."

# === Recherche externe pour un fonds ===
def search_external_info(fund_name_or_cik):
    print(f"\n🔍 Recherche externe pour : {fund_name_or_cik}")
    
    # Recherche par CIK (EDGAR, etc.)
    if fund_name_or_cik.isdigit():
        edgar_data = search_edgar(fund_name_or_cik)
        print(f"🔍 Résultats de la recherche EDGAR :\n{edgar_data}")
    else:
        coinmarketcap_data = search_coinmarketcap(fund_name_or_cik)
        print(f"🔍 Résultats CoinMarketCap :\n{coinmarketcap_data}")
        
        crunchbase_data = search_crunchbase(fund_name_or_cik)
        print(f"🔍 Résultats Crunchbase :\n{crunchbase_data}")
        
        alpha_vantage_data = search_alpha_vantage(fund_name_or_cik)
        print(f"🔍 Résultats Alpha Vantage :\n{alpha_vantage_data}")
