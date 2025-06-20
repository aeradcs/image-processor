import json
import time
from kafka import KafkaConsumer, KafkaProducer
from core.rus_eng_processor import process

# Захардкоженный путь к файлу
HARDCODED_FILE_PATH = '/home/nemo/PycharmProjects/imageProcessor/img_2.png'


def main():
    print("Starting Kafka consumer for image processing...")

    # Пытаемся подключиться к consumer с retry
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

    # Пытаемся подключиться к producer с retry
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
        print(f"\n=== NEW MESSAGE ===")
        print(f"Received message: {message.value}")

        try:
            # Игнорируем содержимое сообщения, используем захардкоженный путь
            print(f"Processing file: {HARDCODED_FILE_PATH}")

            # Используем умный процессор
            lang, text = process(HARDCODED_FILE_PATH)

            print(f"Processing completed successfully!")
            print(f"Detected language: {lang}")
            print(f"Extracted text: {text}...")

            # Формируем успешный ответ
            resp = {
                "status": "ok",
                "error": None,
                "body": {
                    "text": text,
                    "language": lang,
                }
            }

        except Exception as e:
            print(f"Error during processing: {str(e)}")

            # Формируем ответ с ошибкой
            resp = {
                "status": "error",
                "error": str(e),
                "body": {
                    "text": None,
                    "language": None,
                }
            }

        print(f"Sending response with status: {resp['status']}")
        producer.send('image-recognition-responses', resp)
        producer.flush()  # Убеждаемся что сообщение отправлено
        print("Response sent successfully!")
        print("=== MESSAGE PROCESSED ===\n")


if __name__ == "__main__":
    main()