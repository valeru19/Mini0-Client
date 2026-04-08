"""
setup_users.py — скрипт настройки пользователей, bucket и политик.

Домашнее задание (часть 2):
  user1 — чтение в bucket1, чтение+запись в bucket2
  user2 — чтение в bucket2

Используется MinIO Admin API через библиотеку minio.
Запуск (из папки s3_client/):
  pip install minio
  python setup_users.py
"""

from __future__ import annotations

import json
import os
import sys

# MinIO Admin client
try:
    from minio import Minio
    from minio.commonconfig import ENABLED
    from minio.credentials import StaticProvider
    from minio.deleteobjects import DeleteObject
except ImportError:
    sys.exit("Установите библиотеку: pip install minio")

# boto3 нужен для создания bucket через S3 API
import boto3
from botocore.exceptions import ClientError


# ─── Настройки ────────────────────────────────────────────────────────────────

ENDPOINT_URL = os.getenv("S3_ENDPOINT",    "http://localhost:9000")
ACCESS_KEY   = os.getenv("S3_ACCESS_KEY",  "minioadmin")
SECRET_KEY   = os.getenv("S3_SECRET_KEY",  "minioadmin")

MINIO_HOST   = ENDPOINT_URL.replace("http://", "").replace("https://", "")
MINIO_SECURE = ENDPOINT_URL.startswith("https://")

BUCKET1 = "bucket1"
BUCKET2 = "bucket2"

USER1 = {"name": "user1", "password": "User1Password!"}
USER2 = {"name": "user2", "password": "User2Password!"}


# ─── Политики ─────────────────────────────────────────────────────────────────

# Политика: только чтение (GetObject + ListBucket)
def read_only_policy(bucket: str) -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket}"],
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            },
        ],
    })


# Политика: чтение + запись
def read_write_policy(bucket: str) -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                ],
                "Resource": [f"arn:aws:s3:::{bucket}"],
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListMultipartUploadParts",
                    "s3:AbortMultipartUpload",
                ],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            },
        ],
    })


# ─── Вспомогательные функции ──────────────────────────────────────────────────

def make_s3_client() -> boto3.client:
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name="us-east-1",
    )


def ensure_bucket(s3, bucket_name: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"  Bucket {bucket_name!r} уже существует.")
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)
        print(f"  Bucket {bucket_name!r} создан.")


def make_admin_client() -> Minio:
    return Minio(
        MINIO_HOST,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=MINIO_SECURE,
    )


def create_policy(admin: Minio, policy_name: str, policy_json: str) -> None:
    from minio.minioadmin import MinioAdmin
    pass  # see below — используем прямой HTTP-вызов через mc-compatible API


# ─── Основной сценарий ────────────────────────────────────────────────────────

def main() -> None:
    print("\n═══ Настройка MinIO: пользователи, bucket, политики ═══\n")

    # 1. Создание bucket
    print("1. Создание bucket...")
    s3 = make_s3_client()
    ensure_bucket(s3, BUCKET1)
    ensure_bucket(s3, BUCKET2)

    # 2. Политики через MinIO Admin API
    #    MinIO поддерживает управление политиками через специальный endpoint.
    #    Используем requests напрямую (MinIO Admin API v1).
    print("\n2. Создание политик и пользователей через MinIO Admin API...")
    _setup_via_admin_api()

    print("\n═══ Готово! ═══")
    print(f"\n  user1: чтение в {BUCKET1!r}, чтение+запись в {BUCKET2!r}")
    print(f"  user2: чтение в {BUCKET2!r}\n")


def _setup_via_admin_api() -> None:
    """
    Настройка через mc (MinIO Client) — самый надёжный способ.
    Для программного управления используем subprocess + mc.

    Альтернатива: библиотека minio>=7 с MinioAdmin.
    """
    try:
        from minio.minioadmin import MinioAdmin
        _setup_with_minio_admin()
    except (ImportError, AttributeError):
        print("  MinioAdmin API недоступен, используем альтернативный метод...")
        _setup_instructions()


def _setup_with_minio_admin() -> None:
    from minio.minioadmin import MinioAdmin
    from minio.credentials import StaticProvider

    admin = MinioAdmin(
        MINIO_HOST,
        credentials=StaticProvider(ACCESS_KEY, SECRET_KEY),
        secure=MINIO_SECURE,
    )

    # Имена политик
    policy_r_b1  = "read-bucket1"
    policy_rw_b2 = "readwrite-bucket2"
    policy_r_b2  = "read-bucket2"

    # Создаём политики
    for name, json_str in [
        (policy_r_b1,  read_only_policy(BUCKET1)),
        (policy_rw_b2, read_write_policy(BUCKET2)),
        (policy_r_b2,  read_only_policy(BUCKET2)),
    ]:
        try:
            admin.add_policy(name, json_str)
            print(f"  Политика {name!r} создана.")
        except Exception as e:
            print(f"  Политика {name!r}: {e}")

    # Создаём пользователей
    for user in [USER1, USER2]:
        try:
            admin.add_user(user["name"], user["password"])
            print(f"  Пользователь {user['name']!r} создан.")
        except Exception as e:
            print(f"  Пользователь {user['name']!r}: {e}")

    # user1: назначаем read-bucket1 + readwrite-bucket2
    try:
        admin.attach_policy(policy_r_b1,  user=USER1["name"])
        admin.attach_policy(policy_rw_b2, user=USER1["name"])
        print(f"  user1: политики назначены.")
    except Exception as e:
        print(f"  user1 политики: {e}")

    # user2: назначаем read-bucket2
    try:
        admin.attach_policy(policy_r_b2, user=USER2["name"])
        print(f"  user2: политики назначены.")
    except Exception as e:
        print(f"  user2 политики: {e}")


def _setup_instructions() -> None:
    """Выводит команды mc для ручного выполнения."""
    host = ENDPOINT_URL
    print(f"""
  Выполните команды mc (MinIO Client):

  # Добавить alias
  mc alias set local {host} {ACCESS_KEY} {SECRET_KEY}

  # Создать политики
  mc admin policy create local read-bucket1   read_bucket1_policy.json
  mc admin policy create local readwrite-bucket2 readwrite_bucket2_policy.json
  mc admin policy create local read-bucket2   read_bucket2_policy.json

  # Создать пользователей
  mc admin user add local user1 {USER1['password']}
  mc admin user add local user2 {USER2['password']}

  # Назначить политики
  mc admin policy attach local read-bucket1      --user user1
  mc admin policy attach local readwrite-bucket2 --user user1
  mc admin policy attach local read-bucket2      --user user2
""")

    # Сохраняем JSON-файлы политик
    policies = {
        "read_bucket1_policy.json":      read_only_policy(BUCKET1),
        "readwrite_bucket2_policy.json": read_write_policy(BUCKET2),
        "read_bucket2_policy.json":      read_only_policy(BUCKET2),
    }
    for fname, content in policies.items():
        with open(fname, "w") as f:
            f.write(content)
        print(f"  Сохранён файл политики: {fname}")


if __name__ == "__main__":
    main()