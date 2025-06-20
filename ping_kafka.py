# Код для копирования в Python shell
from kafka import KafkaProducer

# Подключаемся к Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: v.encode('utf-8')
)

# Отправляем сообщение
test_message = "ping"
print(f"Sending message: {test_message}")
producer.send('image-recognition-requests', test_message)
producer.flush()
print("Message sent successfully!")

# Закрываем producer
producer.close()