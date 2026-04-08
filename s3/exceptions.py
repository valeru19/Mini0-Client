class S3AppError(Exception):
    """Базовое исключение приложения."""


class BucketNotFoundError(S3AppError):
    """Bucket не найден"""

    def __init__(self, bucket_name: str) -> None:
        super().__init__(f"Bucket {bucket_name!r} не найден")
        self.bucket_name = bucket_name


class BucketAlreadyExistsError(S3AppError):
    """Bucket уже существует"""

    def __init__(self, bucket_name: str) -> None:
        super().__init__(f"Bucket {bucket_name!r} уже существует")
        self.bucket_name = bucket_name


class ObjectNotFoundError(S3AppError):
    """Объект не найден"""

    def __init__(self, bucket: str, key: str) -> None:
        super().__init__(f"Объект {key!r} не найден в bucket {bucket!r}.")
        self.bucket = bucket
        self.key = key


class AccessDeniedError(S3AppError):
    """Отказ в доступе"""

    def __init__(self, message: str = "Доступ запрещён") -> None:
        super().__init__(message)


class S3ConnectionError(S3AppError):
    """Ошибка подключения к S3"""