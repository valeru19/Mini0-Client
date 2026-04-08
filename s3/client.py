from __future__ import annotations

import boto3
from botocore.client import BaseClient

from config.settings import S3Config

class S3Client:
    # Фабрика boto3-клиента. Инкапсулирует параметры подключения
    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._client: BaseClient = self._build_client()

    # Public interface
    @property
    def boto_client(self) -> BaseClient:
        return self._client

    # Private helpersшз
    def _build_client(self) -> BaseClient:
        return boto3.client(
            "s3",
            endpoint_url=self._config.endpoint_url,
            aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key,
            region_name=self._config.region,
            verify=self._config.verify_ssl
        )

    