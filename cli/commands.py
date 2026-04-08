"""
Определения команд CLI.

Отвечает ТОЛЬКО за описание аргументов argparse.
Логика исполнения — в handlers.py.
"""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="s3cli",
        description="Консольный клиент для S3-совместимого хранилища (MinIO / AWS S3).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_EPILOG,
    )

    # Глобальные опции подключения (переопределяют env-переменные)
    parser.add_argument("--endpoint",   metavar="URL",   help="URL S3 (напр. http://localhost:9000)")
    parser.add_argument("--access-key", metavar="KEY",   help="Access Key")
    parser.add_argument("--secret-key", metavar="SECRET",help="Secret Key")
    parser.add_argument("--region",     metavar="REGION",help="Регион (default: us-east-1)")

    subparsers = parser.add_subparsers(dest="command", metavar="КОМАНДА")
    subparsers.required = True

    # ---------- bucket ----------
    _add_bucket_commands(subparsers)

    # ---------- object ----------
    _add_object_commands(subparsers)

    return parser


# ------------------------------------------------------------------
# Bucket sub-commands
# ------------------------------------------------------------------

def _add_bucket_commands(subparsers: argparse._SubParsersAction) -> None:
    # mb — make bucket
    p = subparsers.add_parser("mb", help="Создать bucket")
    p.add_argument("bucket", help="Имя bucket")

    # rb — remove bucket
    p = subparsers.add_parser("rb", help="Удалить bucket")
    p.add_argument("bucket", help="Имя bucket")

    # ls-buckets — list all buckets
    subparsers.add_parser("ls-buckets", help="Список всех bucket")

    # stat-bucket — bucket metadata
    p = subparsers.add_parser("stat-bucket", help="Метаинформация о bucket")
    p.add_argument("bucket", help="Имя bucket")


# ------------------------------------------------------------------
# Object sub-commands
# ------------------------------------------------------------------

def _add_object_commands(subparsers: argparse._SubParsersAction) -> None:
    # ls — list objects
    p = subparsers.add_parser("ls", help="Список объектов в bucket")
    p.add_argument("bucket", help="Имя bucket")
    p.add_argument("--prefix", default="", help="Фильтр по префиксу ключа")

    # stat — object metadata
    p = subparsers.add_parser("stat", help="Метаинформация об объекте")
    p.add_argument("bucket", help="Имя bucket")
    p.add_argument("key",    help="Ключ объекта")

    # put — upload
    p = subparsers.add_parser("put", help="Загрузить файл в bucket")
    p.add_argument("file",   help="Локальный путь к файлу")
    p.add_argument("bucket", help="Имя bucket")
    p.add_argument("key",    nargs="?", help="Ключ объекта (по умолчанию — имя файла)")

    # get — download
    p = subparsers.add_parser("get", help="Скачать объект из bucket")
    p.add_argument("bucket", help="Имя bucket")
    p.add_argument("key",    help="Ключ объекта")
    p.add_argument("dest",   nargs="?", default=".", help="Путь назначения (файл или директория)")


_EPILOG = """
Примеры:
  s3cli mb my-bucket
  s3cli ls-buckets
  s3cli put ./photo.jpg my-bucket
  s3cli put ./photo.jpg my-bucket images/photo.jpg
  s3cli ls my-bucket --prefix images/
  s3cli stat my-bucket images/photo.jpg
  s3cli get my-bucket images/photo.jpg ./downloads/
  s3cli rb my-bucket

Переменные окружения:
  S3_ENDPOINT    URL хранилища   (default: http://localhost:9000)
  S3_ACCESS_KEY  Access Key      (default: minioadmin)
  S3_SECRET_KEY  Secret Key      (default: minioadmin)
  S3_REGION      Регион          (default: us-east-1)
"""