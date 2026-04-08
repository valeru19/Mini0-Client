"""
BucketService — операции с bucket.

Единственная ответственность: создание, удаление,
получение списка и метаинформации о bucket.
"""

from __future__ import annotations

from typing import List

from botocore.exceptions import ClientError

from s3.client import S3Client
from s3.exceptions import (
    AccessDeniedError,
    BucketAlreadyExistsError,
    BucketNotFoundError,
    S3ConnectionError,
)
from s3.models import BucketInfo


class BucketService:
    """Сервис управления bucket"""

    def __init__(self, client: S3Client) -> None:
        self._s3 = client.boto_client

    # Public interface
    def create_bucket(self, bucket_name: str) -> BucketInfo:
        """Создаёт новый bucket"""
        try:
            self._s3.create_bucket(Bucket=bucket_name)
            return BucketInfo(name=bucket_name)
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name)

    def delete_bucket(self, bucket_name: str) -> None:
        """Удаляет bucket (должен быть пустым)"""
        try:
            self._s3.delete_bucket(Bucket=bucket_name)
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name)

    def list_buckets(self) -> List[BucketInfo]:
        """Возвращает список всех доступных bucket"""
        try:
            response = self._s3.list_buckets()
            return [
                BucketInfo(
                    name=b["Name"],
                    creation_date=b.get("CreationDate"),
                )
                for b in response.get("Buckets", [])
            ]
        except ClientError as exc:
            self._handle_client_error(exc)

    def get_bucket_meta(self, bucket_name: str) -> BucketInfo:
        """Возвращает метаинформацию о bucket"""
        try:
            # head_bucket проверяет существование и доступность
            self._s3.head_bucket(Bucket=bucket_name)
            # Дата создания — из list_buckets
            all_buckets = self.list_buckets()
            for b in all_buckets:
                if b.name == bucket_name:
                    return b
            return BucketInfo(name=bucket_name)
        except ClientError as exc:
            self._handle_client_error(exc, bucket_name)

    # Private helpers

    def _handle_client_error(
        self, exc: ClientError, bucket_name: str = ""
    ) -> None:
        code = exc.response["Error"]["Code"]
        if code in ("NoSuchBucket", "404"):
            raise BucketNotFoundError(bucket_name) from exc
        if code in ("BucketAlreadyExists", "BucketAlreadyOwnedByYou"):
            raise BucketAlreadyExistsError(bucket_name) from exc
        if code in ("AccessDenied", "403"):
            raise AccessDeniedError() from exc
        if code == "EndpointConnectionError":
            raise S3ConnectionError(str(exc)) from exc
        raise S3ConnectionError(f"S3 ошибка [{code}]: {exc}") from exc