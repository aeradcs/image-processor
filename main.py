import os
from kafka import KafkaConsumer, KafkaProducer
from PIL import Image
import pytesseract
from langdetect import detect
from pdf2image import convert_from_path
import cv2
import numpy as np
import json
import time

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Захардкоженный путь к файлу
HARDCODED_FILE_PATH = '/home/nemo/PycharmProjects/imageProcessor/img_2.png'


def preprocess_image_for_ocr(image_path):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = cv2.bilateralFilter(img, 11, 17, 17)
    img = cv2.adaptiveThreshold(img, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 2)

    return Image.fromarray(img)


def image_to_text(image: Image.Image) -> str:
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, lang='rus+eng', config=config)


def extract_text_and_lang(file_path):
    try:
        print(f"Processing file: {file_path}")
        images = []

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = preprocess_image_for_ocr(file_path)
            images = [image]
        elif file_path.lower().endswith('.pdf'):
            pages = convert_from_path(file_path, dpi=300)
            images = [Image.fromarray(cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR)) for p in pages]
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        text_blocks = [image_to_text(img) for img in images]
        full_text = "\n".join(text_blocks).strip()

        print(f"Extracted text (first 100 chars): {full_text[:100]}...")

        language = detect(full_text) if full_text else "unknown"
        print(f"Detected language: {language}")

        return full_text, language, None
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return None, None, str(e)


def main():
    print("Starting Kafka consumer...")

    # Пытаемся подключиться с retry
    while True:
        try:
            consumer = KafkaConsumer(
                'image-recognition-requests',
                bootstrap_servers=['localhost:9092'],
                group_id='image-recognition-group',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: m.decode('utf-8')
            )
            print("Consumer connected successfully!")
            break
        except Exception as e:
            print(f"Failed to connect consumer: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Producer connected successfully!")
            break
        except Exception as e:
            print(f"Failed to connect producer: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

    print("Waiting for messages...")

    for message in consumer:
        print(f"\n\nReceived message: {message.value}")

        # Игнорируем содержимое сообщения, используем захардкоженный путь
        text, lang, err = extract_text_and_lang(HARDCODED_FILE_PATH)

        resp = {
            "status": "ok" if err is None else "error",
            "error": err,
            "body": {
                "text": text,
                "language": lang,
            }
        }

        print(f"Sending response: {resp}")
        producer.send('image-recognition-responses', resp)
        producer.flush()  # Убеждаемся что сообщение отправлено
        print("Response sent successfully!")


if __name__ == "__main__":
    main()