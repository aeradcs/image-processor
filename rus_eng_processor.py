from langdetect import detect
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import backup
import backup_eng

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def detect_language_preliminary(file_path):
    """Предварительное определение языка с базовым OCR"""
    try:
        # print("Performing preliminary language detection...")

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file_path)
        elif file_path.lower().endswith('.pdf'):
            pages = convert_from_path(file_path, dpi=200)  # Низкое DPI для скорости
            image = pages[0]
        else:
            raise ValueError("Unsupported file format")

        # Быстрый OCR с базовыми настройками
        config = r'--oem 3 --psm 6'
        preliminary_text = pytesseract.image_to_string(image, lang='rus+eng', config=config)

        # print(f"Preliminary text (first 50 chars): {preliminary_text[:50]}...")

        if preliminary_text.strip():
            detected_lang = detect(preliminary_text)
            # print(f"Preliminary language detection: {detected_lang}")
            return detected_lang
        else:
            # print("No text detected in preliminary scan")
            return "unknown"

    except Exception as e:
        # print(f"Error in preliminary detection: {e}")
        return "unknown"


def process(input_file):
    """
    Единый интерфейс для обработки изображений с автоматическим выбором алгоритма

    Args:
        input_file (str): Путь к файлу изображения или PDF

    Returns:
        tuple: (language, text) - определенный язык и извлеченный текст
    """
    # print(f"Processing file: {input_file}")

    # Этап 1: Предварительное определение языка
    preliminary_lang = detect_language_preliminary(input_file)

    # Этап 2: Выбор процессора на основе определенного языка
    if preliminary_lang == 'ru':
        # print("Using Russian processor...")
        try:
            lang, text = backup.process(input_file)
            # print(f"Russian processor result: lang={lang}, text_length={len(text)}")
            return lang, text
        except Exception as e:
            # print(f"Russian processor failed: {e}")
            # print("Fallback to English processor...")
            return backup_eng.process(input_file)

    elif preliminary_lang == 'en':
        # print("Using English processor...")
        try:
            lang, text = backup_eng.process(input_file)
            # print(f"English processor result: lang={lang}, text_length={len(text)}")
            return lang, text
        except Exception as e:
            # print(f"English processor failed: {e}")
            # print("Fallback to Russian processor...")
            return backup.process(input_file)

    else:
        # print(f"Unknown or unsupported language '{preliminary_lang}', trying both processors...")

        # Пробуем оба процессора и выбираем лучший результат
        results = []

        # Пробуем русский
        try:
            lang, text = backup.process(input_file)
            if text.strip():
                results.append(('russian', lang, text, len(text)))
                # print(f"Russian attempt: lang={lang}, length={len(text)}")
        except Exception as e:
            # print(f"Russian processor failed: {e}")
            pass

        # Пробуем английский
        try:
            lang, text = backup_eng.process(input_file)
            if text.strip():
                results.append(('english', lang, text, len(text)))
                # print(f"English attempt: lang={lang}, length={len(text)}")
        except Exception as e:
            # print(f"English processor failed: {e}")
            pass

        if not results:
            raise ValueError("Both processors failed to extract text")

        # Выбираем результат с наибольшим количеством текста
        best_result = max(results, key=lambda x: x[3])
        processor_used, lang, text, length = best_result
        # print(f"Best result from {processor_used} processor: lang={lang}, length={length}")

        return lang, text


# Для обратной совместимости - функция как в main.py
def extract_text_and_lang(file_path):
    """
    Обертка для совместимости с существующим кодом main.py

    Returns:
        tuple: (text, language, error) - как в оригинальном main.py
    """
    try:
        language, text = process(file_path)
        return text, language, None
    except Exception as e:
        return None, None, str(e)


if __name__ == "__main__":
    # Тест с захардкоженным файлом
    test_file = '/home/nemo/PycharmProjects/imageProcessor/img_3.png'

    print("=== Running rus_eng_processor ===")
    try:
        lang, text = process(test_file)
        print(f"\n\nDetected language: {lang}")
        print(f"Detected text: {text}")
    except Exception as e:
        print(f"Error: {e}")