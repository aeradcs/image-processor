from PIL import Image
import pytesseract
from langdetect import detect
from pdf2image import convert_from_path
import cv2
import numpy as np

# Укажи путь к бинарнику Tesseract (если не system-wide — пропиши свой)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Хардкод пути
file_path = '/home/nemo/PycharmProjects/imageProcessor/img_2.png'

# --- Предобработка изображения ---
def preprocess_image_for_ocr(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # увеличение, шумоподавление, бинаризация
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = cv2.bilateralFilter(img, 11, 17, 17)
    img = cv2.adaptiveThreshold(img, 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 2)

    return Image.fromarray(img)

# --- Распознавание текста ---
def image_to_text(image: Image.Image) -> str:
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, lang='rus+eng', config=config)

# --- Главная логика ---
def extract_text_and_lang(file_path):
    images = []

    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = preprocess_image_for_ocr(file_path)
        images = [image]
    elif file_path.lower().endswith('.pdf'):
        pages = convert_from_path(file_path, dpi=300)
        images = [Image.fromarray(cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR)) for p in pages]
    else:
        raise ValueError("Unsupported file format")

    text_blocks = [image_to_text(img) for img in images]
    full_text = "\n".join(text_blocks).strip()
    language = detect(full_text) if full_text else "unknown"

    return full_text, language

# --- Запуск ---
text, lang = extract_text_and_lang(file_path)
print(f"Detected language: {lang}\n")
print("Recognized text:\n")
print(text)
