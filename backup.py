import pytesseract
from PIL import Image
import os

# Захардкоженный путь к изображению
IMAGE_PATH = "/home/nemo/PycharmProjects/imageProcessor/img.png"


def extract_text_from_image(image_path, lang='rus'):
    """
    Извлекает текст из изображения используя Tesseract OCR

    Args:
        image_path (str): Путь к изображению
        lang (str): Язык для распознавания

    Returns:
        str: Извлеченный текст
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            return f"Ошибка: Файл {image_path} не найден"

        # Открываем изображение
        image = Image.open(image_path)

        # Настройка параметров Tesseract
        custom_config = r'--oem 3 --psm 6'

        # Распознавание текста
        text = pytesseract.image_to_string(image, config=custom_config, lang=lang)

        return text
    except Exception as e:
        return f"Ошибка при обработке изображения: {e}"


def main():
    print("\n===== НАЧАЛО ОБРАБОТКИ ИЗОБРАЖЕНИЯ =====\n")
    print(f"Обрабатываю изображение: {IMAGE_PATH}")

    # Базовое распознавание
    print("\n===== РЕЗУЛЬТАТ РАСПОЗНАВАНИЯ =====\n")
    text = extract_text_from_image(IMAGE_PATH)
    print(text)

    print("\n===== ОБРАБОТКА ЗАВЕРШЕНА =====\n")


if __name__ == "__main__":
    main()