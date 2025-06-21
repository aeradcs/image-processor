import json
import time
import os
import logging
from kafka import KafkaConsumer, KafkaProducer
from dotenv import load_dotenv
from core.rus_eng_processor import process
from aws.s3_client import S3Client

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Kafka consumer for image processing...")

    # Инициализируем S3 клиент
    s3_client = S3Client()

    # Kafka конфигурация из переменных окружения
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')

    # Подключение к consumer с retry
    while True:
        try:
            consumer = KafkaConsumer(
                'image-recognition-requests',
                bootstrap_servers=kafka_servers,
                group_id='image-recognition-group',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            logger.info("Consumer connected successfully!")
            break
        except Exception as e:
            logger.error(f"Failed to connect consumer: {e}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

    # Подключение к producer с retry
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Producer connected successfully!")
            break
        except Exception as e:
            logger.error(f"Failed to connect producer: {e}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

    logger.info("Waiting for messages...")

    for message in consumer:
        file_url = None
        local_file_path = None

        try:
            # Парсим сообщение
            data = message.value
            file_url = data.get('file_url')

            if not file_url:
                raise ValueError("file_url не найден в сообщении")

            logger.info(f"Processing file: {file_url}")

            # Скачиваем файл из S3
            local_file_path = s3_client.download_file(file_url)

            # Обрабатываем файл с помощью OCR
            language, text = process(local_file_path)

            logger.info(f"Processing completed: lang={language}, text_length={len(text)}, text={text}")

            # Формируем успешный ответ
            response = {
                "file_url": file_url,
                "text_detected": text,
                "language_detected": language,
                "status": "success",
                "error_text": None
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing {file_url}: {error_msg}")

            # Формируем ответ с ошибкой
            response = {
                "file_url": file_url,
                "text_detected": None,
                "language_detected": None,
                "status": "error",
                "error_text": error_msg
            }

        finally:
            # Очищаем временный файл
            if local_file_path:
                s3_client.cleanup_file(local_file_path)

        # Отправляем ответ
        try:
            producer.send('image-recognition-responses', response)
            producer.flush()
            logger.info(f"Response sent for {file_url}")
        except Exception as e:
            logger.error(f"Failed to send response: {e}")


if __name__ == "__main__":
    main()