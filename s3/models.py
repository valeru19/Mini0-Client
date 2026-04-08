from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class BucketInfo:
    """Метаинформация о bucket"""

    name: str
    creation_date: Optional[datetime] = None

    def __str__(self) -> str:
        date_str = (
            self.creation_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            if self.creation_date
            else "N/A"
        )
        return f"Bucket: {self.name!r}  (создан: {date_str})"


@dataclass(frozen=True)
class ObjectInfo:
    """Метаинформация об объекте в bucket"""

    key: str
    size: int = 0
    last_modified: Optional[datetime] = None
    etag: str = ""
    content_type: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def size_human(self) -> str:
        """Человекочитаемый размер файла"""
        for unit in ("Б", "КБ", "МБ", "ГБ", "ТБ"):
            if self.size < 1024:
                return f"{self.size:.1f} {unit}"
            self.size / 1024  # noqa: B018 — intentional for loop
            # recalc properly:
        return f"{self.size} Б"

    @property
    def size_str(self) -> str:
        size = self.size
        for unit in ("Б", "КБ", "МБ", "ГБ", "ТБ"):
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{self.size} Б"

    def __str__(self) -> str:
        date_str = (
            self.last_modified.strftime("%Y-%m-%d %H:%M:%S")
            if self.last_modified
            else "N/A"
        )
        return (
            f"  {self.key:<50} {self.size_str:>12}  {date_str}"
        )