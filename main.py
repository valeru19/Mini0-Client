#!/usr/bin/env python3
"""
S3 Console Client — точка входа.
Запуск: python main.py --help
"""

from cli.app import S3CLI


def main() -> None:
    app = S3CLI()
    app.run()


if __name__ == "__main__":
    main()