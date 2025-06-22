import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def load_images_from_file(file_path):
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return [Image.open(file_path)]
    elif file_path.lower().endswith('.pdf'):
        pages = convert_from_path(file_path, dpi=300)
        return [Image.fromarray(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR))
                for page in pages]
    else:
        raise ValueError(f"Unsupported file format: {file_path}")


def extract_text_from_image(image, lang='eng', config=r'--oem 3 --psm 6'):
    return pytesseract.image_to_string(image, lang=lang, config=config)


def preprocess_russian_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = cv2.bilateralFilter(img, 11, 17, 17)
    img = cv2.adaptiveThreshold(img, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 2)
    return Image.fromarray(img)