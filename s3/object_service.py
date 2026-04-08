"""
ObjectService — операции с объектами внутри bucket.

Единственная ответственность: список объектов,
загрузка, скачивание, метаинформация.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from botocore.exceptions import ClientError

from s3.client import S3Client
from s3.exceptions import (
    AccessDeniedError,
    BucketNotFoundError,
    ObjectNotFoundError,
    S3ConnectionError,
)
from s3.models import ObjectInfo


class ObjectService:
    """Сервис управления объектами в bucket"""

    def __init__(self, client: S3Client) -> None:
        self._s3 = client.boto_client

    # Public interface
    def list_objects(self, bucket_name: str, prefix: str = "") -> List[ObjectInfo]:
        """Возвращает список объектов в bucket (с опциональным prefix)"""
        try:
            paginator = self._s3.get_paginator("list_objects_v2")
            kwargs = {"Bucket": bucket_name}
            if prefix:
                kwargs["Prefix"] = prefix

            objects: List[ObjectInfo] = []
            for page in paginator.paginate(**kwargs):
                for obj in page.get("Contents", []):
                    objects.append(
                        ObjectInfo(
                            key=obj["Key"],
                            size=obj.get("Size", 0),
                            last_modified=obj.get("LastModified"),
                            etag=obj.get("ETag", "").strip('"'),
                        )
                    )
            return objects
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name)

    def get_object_meta(self, bucket_name: str, key: str) -> ObjectInfo:
        """Возвращает метаинформацию об объекте (HEAD запрос)"""
        try:
            resp = self._s3.head_object(Bucket=bucket_name, Key=key)
            return ObjectInfo(
                key=key,
                size=resp.get("ContentLength", 0),
                last_modified=resp.get("LastModified"),
                etag=resp.get("ETag", "").strip('"'),
                content_type=resp.get("ContentType", ""),
                metadata=resp.get("Metadata", {}),
            )
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name, key)

    def upload_object(
        self,
        bucket_name: str,
        key: str,
        file_path: str,
        extra_metadata: dict | None = None,
    ) -> ObjectInfo:
        """
        Загружает файл в bucket

        :param bucket_name: имя bucket
        :param key:         ключ объекта в хранилище
        :param file_path:   путь к локальному файлу
        :param extra_metadata: пользовательские метаданные (dict str→str)
        """
        local_path = Path(file_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        extra_args: dict = {}
        if extra_metadata:
            extra_args["Metadata"] = extra_metadata

        try:
            self._s3.upload_file(
                Filename=str(local_path),
                Bucket=bucket_name,
                Key=key,
                ExtraArgs=extra_args if extra_args else None,
            )
            return self.get_object_meta(bucket_name, key)
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name, key)

    def download_object(
        self, bucket_name: str, key: str, dest_path: str
    ) -> Path:
        """
        Скачивает объект в локальный файл

        :param dest_path: путь назначения; если директория — файл
                          сохраняется под именем ключа.
        :returns: реальный путь сохранённого файла.
        """
        destination = Path(dest_path)
        if destination.is_dir():
            destination = destination / Path(key).name

        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._s3.download_file(
                Bucket=bucket_name, Key=key, Filename=str(destination)
            )
            return destination
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name, key)

    
    # Private helpers

    def _handle_client_error(
        self,
        exc: ClientError,
        bucket_name: str = "",
        key: str = "",
    ) -> None:
        code = exc.response["Error"]["Code"]
        if code in ("NoSuchBucket", "404") and not key:
            raise BucketNotFoundError(bucket_name) from exc
        if code in ("NoSuchKey", "404"):
            raise ObjectNotFoundError(bucket_name, key) from exc
        if code in ("AccessDenied", "403"):
            raise AccessDeniedError() from exc
        raise S3ConnectionError(f"S3 ошибка [{code}]: {exc}") from exc