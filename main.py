import pytesseract
from PIL import Image
import os

# Захардкоженный путь к изображению
IMAGE_PATH = "/home/nemo/PycharmProjects/imageProcessor/img_3.png"


def extract_text_with_optimal_params(image_path):
    """
    Извлекает текст из изображения используя оптимальные параметры для каждого языка

    Args:
        image_path (str): Путь к изображению

    Returns:
        dict: Результаты распознавания для каждой конфигурации
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            return {"error": f"Файл {image_path} не найден"}

        # Открываем изображение
        image = Image.open(image_path)

        results = {}

        # Оптимальная конфигурация для русского текста
        custom_config_rus = r'--oem 3 --psm 6'
        text_rus = pytesseract.image_to_string(image, config=custom_config_rus, lang='rus')
        results["rus_оптимальный"] = text_rus

        # Оптимальная конфигурация для английского текста
        custom_config_eng = r'--oem 1 --psm 4'
        text_eng = pytesseract.image_to_string(image, config=custom_config_eng, lang='eng')
        results["eng_оптимальный"] = text_eng

        # Определяем язык изображения
        try:
            lang_detect = pytesseract.image_to_osd(image)
            results["определение_языка"] = lang_detect
        except:
            results["определение_языка"] = "Не удалось определить язык"

        return results
    except Exception as e:
        return {"error": f"Ошибка при обработке изображения: {e}"}


def main():
    print("\n===== НАЧАЛО ОБРАБОТКИ ИЗОБРАЖЕНИЯ =====\n")
    print(f"Обрабатываю изображение: {IMAGE_PATH}")

    # Получаем результаты с оптимальными параметрами
    results = extract_text_with_optimal_params(IMAGE_PATH)

    # Выводим результаты
    for config_name, text in results.items():
        print(f"\n===== РЕЗУЛЬТАТ ({config_name}) =====\n")
        print(text)

    print("\n===== ОБРАБОТКА ЗАВЕРШЕНА =====\n")

    print("\n===== РЕКОМЕНДАЦИИ =====\n")
    print("Для русских документов используйте параметры: --oem 3 --psm 6 lang='rus'")
    print("Для английских документов используйте параметры: --oem 1 --psm 4 lang='eng'")
    print("Для смешанных документов выбирайте конфигурацию в зависимости от преобладающего языка")


if __name__ == "__main__":
    main()