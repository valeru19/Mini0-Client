"""
Handlers — исполнение команд CLI.

Каждый handler получает готовые сервисы через DI,
вызывает их методы и форматирует вывод через Formatter.
Не содержит бизнес-логики — только «оркестрацию».
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cli.formatter import Formatter
from s3.bucket_service import BucketService
from s3.exceptions import S3AppError
from s3.object_service import ObjectService


class CommandHandlers:
    """Набор обработчиков команд CLI."""

    def __init__(
        self,
        bucket_service: BucketService,
        object_service: ObjectService,
        formatter: Formatter,
    ) -> None:
        self._buckets  = bucket_service
        self._objects  = object_service
        self._fmt      = formatter

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch(self, args: argparse.Namespace) -> int:
        """Вызывает нужный handler по args.command. Возвращает exit code."""
        try:
            return self._dispatch_inner(args)
        except S3AppError as exc:
            print(self._fmt.error(str(exc)))
            return 1
        except FileNotFoundError as exc:
            print(self._fmt.error(str(exc)))
            return 1

    def _dispatch_inner(self, args: argparse.Namespace) -> int:
        handlers = {
            "mb":          self._create_bucket,
            "rb":          self._delete_bucket,
            "ls-buckets":  self._list_buckets,
            "stat-bucket": self._stat_bucket,
            "ls":          self._list_objects,
            "stat":        self._stat_object,
            "put":         self._upload_object,
            "get":         self._download_object,
        }
        handler = handlers.get(args.command)
        if not handler:
            print(self._fmt.error(f"Неизвестная команда: {args.command}"))
            return 1
        return handler(args)

    # ------------------------------------------------------------------
    # Bucket handlers
    # ------------------------------------------------------------------

    def _create_bucket(self, args: argparse.Namespace) -> int:
        self._buckets.create_bucket(args.bucket)
        print(self._fmt.success(f"Bucket {args.bucket!r} создан."))
        return 0

    def _delete_bucket(self, args: argparse.Namespace) -> int:
        self._buckets.delete_bucket(args.bucket)
        print(self._fmt.success(f"Bucket {args.bucket!r} удалён."))
        return 0

    def _list_buckets(self, args: argparse.Namespace) -> int:
        buckets = self._buckets.list_buckets()
        print(self._fmt.format_buckets(buckets))
        return 0

    def _stat_bucket(self, args: argparse.Namespace) -> int:
        meta = self._buckets.get_bucket_meta(args.bucket)
        print(self._fmt.format_bucket_meta(meta))
        return 0

    # ------------------------------------------------------------------
    # Object handlers
    # ------------------------------------------------------------------

    def _list_objects(self, args: argparse.Namespace) -> int:
        objects = self._objects.list_objects(args.bucket, prefix=args.prefix)
        print(self._fmt.format_objects(objects, args.bucket))
        return 0

    def _stat_object(self, args: argparse.Namespace) -> int:
        meta = self._objects.get_object_meta(args.bucket, args.key)
        print(self._fmt.format_object_meta(meta, args.bucket))
        return 0

    def _upload_object(self, args: argparse.Namespace) -> int:
        key = args.key or Path(args.file).name
        meta = self._objects.upload_object(args.bucket, key, args.file)
        print(self._fmt.success(
            f"Загружено: {args.file!r} → {args.bucket!r}/{key}  ({meta.size_str})"
        ))
        return 0

    def _download_object(self, args: argparse.Namespace) -> int:
        dest = self._objects.download_object(args.bucket, args.key, args.dest)
        print(self._fmt.success(
            f"Скачано: {args.bucket!r}/{args.key} → {dest}"
        ))
        return 0