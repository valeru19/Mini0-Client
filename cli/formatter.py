"""
Formatter — слой представления.

Отвечает исключительно за форматирование вывода в консоль.
Бизнес-логика и сервисы ничего не знают об этом классе.
"""

from __future__ import annotations

from typing import List

from s3.models import BucketInfo, ObjectInfo


class Formatter:
    """Форматирует объекты домена для вывода в терминал."""

    # ANSI-коды цветов
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[32m"
    CYAN   = "\033[36m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    GREY   = "\033[90m"

    # ------------------------------------------------------------------

    def header(self, text: str) -> str:
        return f"\n{self.BOLD}{self.CYAN}{'─' * 60}{self.RESET}\n" \
               f" {self.BOLD}{text}{self.RESET}\n" \
               f"{self.GREY}{'─' * 60}{self.RESET}"

    def success(self, text: str) -> str:
        return f"{self.GREEN}✓  {text}{self.RESET}"

    def error(self, text: str) -> str:
        return f"{self.RED}✗  {text}{self.RESET}"

    def info(self, text: str) -> str:
        return f"{self.YELLOW}ℹ  {text}{self.RESET}"

    # ------------------------------------------------------------------

    def format_buckets(self, buckets: List[BucketInfo]) -> str:
        if not buckets:
            return self.info("Нет доступных bucket.")
        lines = [self.header(f"Bucket-ы ({len(buckets)})")]
        for b in buckets:
            date_str = (
                b.creation_date.strftime("%Y-%m-%d %H:%M") if b.creation_date else "N/A"
            )
            lines.append(
                f"  {self.BOLD}{self.CYAN}{b.name:<40}{self.RESET}"
                f"  {self.GREY}{date_str}{self.RESET}"
            )
        return "\n".join(lines)

    def format_bucket_meta(self, bucket: BucketInfo) -> str:
        lines = [self.header(f"Метаинформация: {bucket.name}")]
        lines.append(f"  {'Название':<20} {self.BOLD}{bucket.name}{self.RESET}")
        date_str = (
            bucket.creation_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            if bucket.creation_date
            else "N/A"
        )
        lines.append(f"  {'Дата создания':<20} {date_str}")
        return "\n".join(lines)

    def format_objects(self, objects: List[ObjectInfo], bucket: str) -> str:
        if not objects:
            return self.info(f"Bucket {bucket!r} пуст.")
        lines = [self.header(f"Объекты в '{bucket}' ({len(objects)})")]
        lines.append(
            f"  {self.GREY}{'Ключ':<50} {'Размер':>12}  {'Изменён'}{self.RESET}"
        )
        lines.append(f"  {self.GREY}{'─' * 78}{self.RESET}")
        for obj in objects:
            date_str = (
                obj.last_modified.strftime("%Y-%m-%d %H:%M")
                if obj.last_modified
                else "N/A"
            )
            lines.append(
                f"  {self.CYAN}{obj.key:<50}{self.RESET}"
                f"  {obj.size_str:>12}"
                f"  {self.GREY}{date_str}{self.RESET}"
            )
        return "\n".join(lines)

    def format_object_meta(self, obj: ObjectInfo, bucket: str) -> str:
        lines = [self.header(f"Метаинформация: {bucket}/{obj.key}")]
        lines.append(f"  {'Ключ':<20} {self.BOLD}{obj.key}{self.RESET}")
        lines.append(f"  {'Размер':<20} {obj.size_str}")
        date_str = (
            obj.last_modified.strftime("%Y-%m-%d %H:%M:%S UTC")
            if obj.last_modified
            else "N/A"
        )
        lines.append(f"  {'Изменён':<20} {date_str}")
        lines.append(f"  {'ETag':<20} {self.GREY}{obj.etag}{self.RESET}")
        lines.append(f"  {'Content-Type':<20} {obj.content_type or 'N/A'}")
        if obj.metadata:
            lines.append(f"  {'Метаданные':<20}")
            for k, v in obj.metadata.items():
                lines.append(f"    {self.YELLOW}{k}{self.RESET}: {v}")
        return "\n".join(lines)