from langdetect import detect
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from core import russian_ocr, english_ocr

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def detect_language_preliminary(file_path):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file_path)
        elif file_path.lower().endswith('.pdf'):
            pages = convert_from_path(file_path, dpi=200)
            image = pages[0]
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        config = r'--oem 3 --psm 6'
        preliminary_text = pytesseract.image_to_string(image, lang='rus+eng', config=config)

        if preliminary_text.strip():
            return detect(preliminary_text)
        return "unknown"

    except Exception:
        return "unknown"


def process(input_file):
    preliminary_lang = detect_language_preliminary(input_file)

    if preliminary_lang == 'ru':
        try:
            lang, text = russian_ocr.process(input_file)
            if text.strip():
                actual_lang = detect(text)
                return actual_lang, text
            return lang, text
        except Exception:
            return english_ocr.process(input_file)

    elif preliminary_lang == 'en':
        try:
            lang, text = english_ocr.process(input_file)
            if text.strip():
                actual_lang = detect(text)
                return actual_lang, text
            return lang, text
        except Exception:
            return russian_ocr.process(input_file)

    else:
        # Unknown language - try both processors
        results = []

        try:
            lang, text = russian_ocr.process(input_file)
            if text.strip():
                results.append(('russian', lang, text, len(text)))
        except Exception:
            pass

        try:
            lang, text = english_ocr.process(input_file)
            if text.strip():
                results.append(('english', lang, text, len(text)))
        except Exception:
            pass

        if not results:
            raise ValueError("Both processors failed to extract text")

        # Choose result with most text content
        best_result = max(results, key=lambda x: x[3])
        _, lang, text, _ = best_result

        return lang, text


def extract_text_and_lang(file_path):
    try:
        language, text = process(file_path)
        return text, language, None
    except Exception as e:
        return None, None, str(e)