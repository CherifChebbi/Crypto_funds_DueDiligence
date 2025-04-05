import pytesseract
from pdf2image import convert_from_path
import os
from PIL import Image

def extract_text_ocr(pdf_path, dpi=300):
    text = ""
    images = convert_from_path(pdf_path, dpi=dpi)
    for i, img in enumerate(images):
        gray = img.convert('L')  # Conversion en niveaux de gris
        text += pytesseract.image_to_string(gray, lang='eng') + "\n"
    return text.strip()
