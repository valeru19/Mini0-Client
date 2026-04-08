"""
S3CLI — корень композиции (Composition Root).

Здесь происходит сборка всего графа зависимостей:
Config → S3Client → Services → Handlers → CLI.

Принцип: зависимости создаются ОДИН РАЗ в одном месте,
а не внутри каждого класса (Dependency Injection).
"""

from __future__ import annotations

import sys

from cli.commands import build_parser
from cli.formatter import Formatter
from cli.handlers import CommandHandlers
from config.settings import S3Config
from s3.bucket_service import BucketService
from s3.client import S3Client
from s3.object_service import ObjectService


class S3CLI:
    """
    Главное приложение.
    Собирает зависимости и запускает CLI.
    """

    def __init__(self) -> None:
        self._parser = build_parser()

    def run(self) -> None:
        args = self._parser.parse_args()

        # --- Конфигурация: CLI-аргументы перекрывают env-переменные ---
        import os
        if args.endpoint:
            os.environ["S3_ENDPOINT"] = args.endpoint
        if args.access_key:
            os.environ["S3_ACCESS_KEY"] = args.access_key
        if args.secret_key:
            os.environ["S3_SECRET_KEY"] = args.secret_key
        if args.region:
            os.environ["S3_REGION"] = args.region

        # --- Граф зависимостей ---
        config   = S3Config()
        client   = S3Client(config)
        buckets  = BucketService(client)
        objects  = ObjectService(client)
        fmt      = Formatter()
        handlers = CommandHandlers(buckets, objects, fmt)

        exit_code = handlers.dispatch(args)
        sys.exit(exit_code)