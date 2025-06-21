from kafka import KafkaProducer
import json

# Подключаемся к Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Тестовые файлы из вашего S3 bucket
test_files = [
    "https://672421063581-images-for-ocr.s3.us-east-1.amazonaws.com/img.png",
    "https://672421063581-images-for-ocr.s3.us-east-1.amazonaws.com/img_1.png",
    "https://672421063581-images-for-ocr.s3.us-east-1.amazonaws.com/img_2.png",
    "https://672421063581-images-for-ocr.s3.us-east-1.amazonaws.com/img_3.png"
]

# Выберите какой файл тестировать (можно изменить индекс)
selected_file = test_files[0]  # img.png

# Формируем сообщение
test_message = {
    "file_url": selected_file
}

print(f"Sending message: {test_message}")
producer.send('image-recognition-requests', test_message)
producer.flush()
print("Message sent successfully!")

# Закрываем producer
producer.close()

print(f"\nДля тестирования других файлов измените индекс в test_files:")
for i, file in enumerate(test_files):
    print(f"  {i}: {file.split('/')[-1]}")