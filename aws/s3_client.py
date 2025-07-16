import boto3
import os
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse
import logging


class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.temp_dir = Path(tempfile.gettempdir()) / 'ocr_temp'
        self.temp_dir.mkdir(exist_ok=True)
        logging.error(f"==============S3================ init === self.temp_dir {self.temp_dir}")

    def parse_s3_url(self, s3_url):
        """Парсит S3 URL и возвращает bucket_name и object_key"""
        parsed = urlparse(s3_url)
        logging.error(f"==============S3================ parse_s3_url === parsed url {parsed}")


        if parsed.scheme == 's3':
            # s3://bucket-name/path/file.jpg
            bucket_name = parsed.netloc
            object_key = parsed.path.lstrip('/')
            logging.error(f"==============S3================ parse_s3_url === scheme s3 bucket_name {bucket_name} object_key {object_key}")

        elif parsed.scheme in ['http', 'https']:
            # https://bucket-name.s3.region.amazonaws.com/path/file.jpg
            # или https://s3.region.amazonaws.com/bucket-name/path/file.jpg
            host_parts = parsed.netloc.split('.')
            if 's3' in host_parts:
                if host_parts[0] != 's3':
                    # bucket-name.s3.region.amazonaws.com
                    bucket_name = host_parts[0]
                else:
                    # s3.region.amazonaws.com/bucket-name/file.jpg
                    path_parts = parsed.path.strip('/').split('/', 1)
                    bucket_name = path_parts[0]
                    object_key = path_parts[1] if len(path_parts) > 1 else ''
                    return bucket_name, object_key
            else:
                raise ValueError(f"Неподдерживаемый формат S3 URL: {s3_url}")
            object_key = parsed.path.lstrip('/')
            logging.error(f"==============S3================ parse_s3_url === scheme https bucket_name {bucket_name} object_key {object_key}")
        else:
            logging.error(f"==============S3================ parse_s3_url === err Неподдерживаемая схема UR")
            raise ValueError(f"Неподдерживаемая схема URL: {parsed.scheme}")

        return bucket_name, object_key

    def download_file(self, s3_url):
        """Скачивает файл из S3 по URL во временную папку"""
        try:
            # Парсим URL
            bucket_name, object_key = self.parse_s3_url(s3_url)
            logging.error(f"==============S3================ download_file === bucket_name {bucket_name} object_key {object_key}")


            # Создаем уникальное имя временного файла
            file_extension = Path(object_key).suffix
            temp_filename = f"{uuid.uuid4()}{file_extension}"
            local_path = self.temp_dir / temp_filename
            logging.error(f"==============S3================ download_file === file_extension {file_extension} temp_filename {temp_filename} local_path {local_path}")

            # Скачиваем файл
            self.s3_client.download_file(bucket_name, object_key, str(local_path))
            logging.error(f"==============S3================ download_file === Downloaded {s3_url} to {local_path}")

            # logging.info(f"Downloaded {s3_url} to {local_path}")
            return str(local_path)

        except Exception as e:
            # logging.error(f"Failed to download {s3_url}: {e}")
            logging.error(f"==============S3================ download_file === err {str(e)}")

            raise Exception(f"Ошибка скачивания файла из S3: {str(e)}")

    def cleanup_file(self, local_path):
        """Удаляет временный файл"""
        try:
            logging.error(f"==============S3================ cleanup_file === local_path and Path(local_path).exists() {local_path and Path(local_path).exists()}")

            if local_path and Path(local_path).exists():
                Path(local_path).unlink()
                # logging.info(f"Cleaned up temporary file: {local_path}")
        except Exception as e:
            logging.error(f"==============S3================ cleanup_file === err {str(e)}")

            # logging.warning(f"Failed to cleanup {local_path}: {e}")