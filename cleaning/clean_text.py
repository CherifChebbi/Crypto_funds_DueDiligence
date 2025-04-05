import re
import unicodedata

def clean_text(text):
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Supprimer les caractères spéciaux inutiles
    text = re.sub(r"[^\w\s.,:%€$-]", " ", text)

    # Convertir en minuscules
    text = text.lower()

    # Supprimer les espaces multiples et lignes vides
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n", "\n", text)

    # Trim final
    return text.strip()
