import boto3
import os
from dotenv import load_dotenv

# Загружаем .env и подключаемся к AWS
load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket_name = os.getenv('S3_BUCKET_NAME')

# Список bucket'ов
try:
    buckets = s3.list_buckets()
    print("Ваши bucket'ы:")
    for bucket in buckets['Buckets']:
        print(f"  - {bucket['Name']}")
except Exception as e:
    print(f"Ошибка списка bucket'ов: {e}")

# Список файлов в вашем bucket
try:
    response = s3.list_objects_v2(Bucket=bucket_name)
    print(f"\nФайлы в '{bucket_name}':")
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"  - {obj['Key']} ({obj['Size']} байт)")
    else:
        print("  Bucket пустой")
except Exception as e:
    print(f"Ошибка доступа к bucket: {e}")

print(f"\nS3 клиент готов к использованию (переменная 's3')")
print(f"Имя bucket: {bucket_name}")