from kafka import KafkaConsumer
import json


# Скрипт для мониторинга ответов из Python сервиса
def main():
    print("Listening for responses from image processing service...")

    try:
        consumer = KafkaConsumer(
            'image-recognition-responses',
            bootstrap_servers=['localhost:9092'],
            group_id='test-consumer-group',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        print("Connected to Kafka. Waiting for responses...")

        for message in consumer:
            print("\n" + "=" * 50)
            print("RECEIVED RESPONSE:")
            response = message.value

            print(f"File URL: {response.get('file_url')}")
            print(f"Status: {response.get('status')}")
            print(f"Language: {response.get('language_detected')}")
            print(f"Error: {response.get('error_text')}")

            text = response.get('text_detected')
            if text:
                print(f"Text: {text}...")
            else:
                print("Text: None")

            print("=" * 50)

    except KeyboardInterrupt:
        print("\nStopping consumer...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()