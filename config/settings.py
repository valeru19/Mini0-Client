from __future__ import annotations
import os
from dataclasses import dataclass, field



@dataclass
class S3Config:
    # Все параметры подключения к S3

    endpoint_url: str = field(
        default_factory=lambda: os.getevn("S3_ENDPOINT", "http://localhost:9000")
    )

    access_key: str = field(
        default_factory=lambda: os.getevn("S3_ACCESS_KEY", "minioadmin")
    )

    secret_key: str = field(
        default_factory=lambda: os.getevn("S3_SECTRET_KEY", "minioadmin")
    )

    region: str = field(
        default_factory=lambda: os.getevn("S3_REGION", "us-east-1")
    )
    verify_ssl: bool = field(
        default_factory=lambda: os.getevn("S3_VERIFY_SSL", "false").lower() == "true"
    )

    def __post_init__(self) -> None:
        if not self.endpoint_url:
            raise ValueError("S3_ENDPOINT не задан")
        if not self.access_key or not self.secret_key:
            raise("S3_ACCESS_KEY/S3_SECTRET_KEY не заданы")

