import pytesseract
from PIL import Image
import os
from langdetect import detect

# Захардкоженный путь к изображению
IMAGE_PATH = "/home/nemo/PycharmProjects/imageProcessor/img_1.png"


def extract_text_from_image(image_path, lang='eng', oem=1, psm=4):
    """
    Извлекает текст из изображения используя Tesseract OCR

    Args:
        image_path (str): Путь к изображению
        lang (str): Язык для распознавания
        oem (int): Режим OCR-движка (0-3)
        psm (int): Режим сегментации страницы (0-13)

    Returns:
        str: Извлеченный текст
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            return f"Ошибка: Файл {image_path} не найден"

        # Открываем изображение
        image = Image.open(image_path)

        # Настройка параметров Tesseract для английского текста
        # --psm 4: Предполагаем один столбец текста переменной высоты
        # --oem 1: Используем только LSTM движок (часто лучше для английского)
        custom_config = f'--oem {oem} --psm {psm}'

        # Распознавание текста
        text = pytesseract.image_to_string(image, config=custom_config, lang=lang)

        return text
    except Exception as e:
        return f"Ошибка при обработке изображения: {e}"


def try_different_configs(image_path):
    """
    Пробует различные конфигурации для улучшения распознавания английского текста
    """
    results = {}

    # Пробуем разные режимы сегментации страницы для английского языка
    for psm in [1, 3, 4, 6, 11]:
        for oem in [1, 3]:
            config_name = f"eng_oem{oem}_psm{psm}"
            text = extract_text_from_image(image_path, 'eng', oem, psm)
            results[config_name] = text

    return results


# --- НОВАЯ ФУНКЦИЯ ДЛЯ ЕДИНОГО ИНТЕРФЕЙСА ---
def process(input_file):
    """
    Единый интерфейс для английского процессора

    Args:
        input_file (str): Путь к файлу

    Returns:
        tuple: (lang, text) - язык и текст
    """
    # Пробуем различные конфигурации
    results = try_different_configs(input_file)

    # Находим самый длинный результат (предположительно лучший)
    best_config = max(results.items(), key=lambda x: len(x[1]))[0]
    best_text = results[best_config]

    # Определяем язык
    language = detect(best_text) if best_text.strip() else "unknown"

    return language, best_text


def main():
    print("\n===== НАЧАЛО ОБРАБОТКИ ИЗОБРАЖЕНИЯ =====\n")
    print(f"Обрабатываю изображение: {IMAGE_PATH}")

    # Пробуем различные конфигурации
    results = try_different_configs(IMAGE_PATH)

    # Находим самый длинный результат (предположительно лучший)
    best_config = max(results.items(), key=lambda x: len(x[1]))[0]
    best_text = results[best_config]

    print(f"\n===== ЛУЧШИЙ РЕЗУЛЬТАТ ({best_config}) =====\n")
    print(best_text)

    print("\n===== ОБРАБОТКА ЗАВЕРШЕНА =====\n")


if __name__ == "__main__":
    main()