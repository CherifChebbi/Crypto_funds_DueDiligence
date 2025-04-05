import os
import re
import json
from pathlib import Path
from dateparser import search as date_search

OUTPUT_DIR = "output"

# === REGEX patterns ===
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
URL_REGEX = r"https?://[^\s]+"
CIK_REGEX = r"CIK[:\s]+(\d{10})"

def extract_entities(text):
    #Ajouter un log ici pour indiquer qu'on commence l'extraction des entités
    print("Début de l'extraction des entités...")
    
    emails = re.findall(EMAIL_REGEX, text)
    urls = re.findall(URL_REGEX, text)
    ciks = re.findall(CIK_REGEX, text)
    dates = [str(dt_tuple[1].date()) for dt_tuple in date_search.search_dates(text) or []]

    return {
        "emails": list(set(emails)),
        "urls": list(set(urls)),
        "ciks": list(set(ciks)),
        "dates": list(set(dates)),
    }

def process_cleaned_files():
    for folder in os.listdir(OUTPUT_DIR):
        folder_path = os.path.join(OUTPUT_DIR, folder)
        #cleaned_txt_path = os.path.join(folder_path, "cleaned.txt")
        cleaned_txt_path = os.path.join(folder_path, "raw_text.txt")


        if not os.path.exists(cleaned_txt_path):
            continue

        with open(cleaned_txt_path, "r", encoding="utf-8") as f:
            cleaned_text = f.read()

        entities = extract_entities(cleaned_text)

        with open(os.path.join(folder_path, "metadata_extracted.json"), "w", encoding="utf-8") as f:
            json.dump(entities, f, indent=4, ensure_ascii=False)

        print(f"[✓] Entités extraites pour {folder} → metadata_extracted.json")

if __name__ == "__main__":
    process_cleaned_files()
