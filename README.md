# S3 Console Client

Консольный клиент для S3-совместимого хранилища (MinIO / AWS S3).

## Архитектура

```
s3_client/
├── main.py                    # Точка входа
├── config/
│   └── settings.py            # S3Config — параметры подключения
├── s3/
│   ├── client.py              # S3Client — boto3-фабрика (низкий уровень)
│   ├── bucket_service.py      # BucketService — операции с bucket
│   ├── object_service.py      # ObjectService — операции с объектами
│   ├── models.py              # BucketInfo, ObjectInfo (Value Objects)
│   └── exceptions.py          # Иерархия исключений приложения
├── cli/
│   ├── app.py                 # S3CLI — Composition Root / DI
│   ├── commands.py            # argparse — описание команд
│   ├── handlers.py            # CommandHandlers — исполнение команд
│   └── formatter.py           # Formatter — форматирование вывода
├── setup_users.py             # Скрипт настройки пользователей и политик
├── docker-compose.yml
└── requirements.txt
```

### Применённые принципы ООП и архитектуры

| Принцип | Где применён |
|---------|-------------|
| **SRP** (Single Responsibility) | `BucketService` — только bucket; `ObjectService` — только объекты; `Formatter` — только вывод |
| **OCP** (Open/Closed) | Новые команды добавляются в `commands.py` + метод в `handlers.py` без изменения существующего кода |
| **DIP** (Dependency Inversion) | Все сервисы получают `S3Client` через конструктор (DI), не создают сами |
| **Composition Root** | `S3CLI.run()` — единственное место создания всего графа зависимостей |
| **Value Objects** | `BucketInfo`, `ObjectInfo` — неизменяемые (`frozen=True`) объекты данных |
| **Exception Hierarchy** | Собственные исключения; сервисы не пробрасывают boto3-исключения наружу |
| **Separation of Concerns** | CLI отделён от бизнес-логики; форматирование — отдельный класс |

---

## Быстрый старт

### 1. Запустить MinIO

```bash
docker-compose up -d
```

Web-консоль: http://localhost:9001 (minioadmin / minioadmin)

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Использование

```bash
# Из папки s3_client/
cd s3_client

# Создать bucket
python main.py mb my-bucket

# Загрузить файл
python main.py put ./README.md my-bucket

# Список объектов
python main.py ls my-bucket

# Метаинформация об объекте
python main.py stat my-bucket README.md

# Метаинформация о bucket
python main.py stat-bucket my-bucket

# Скачать объект
python main.py get my-bucket README.md ./downloads/

# Список всех bucket
python main.py ls-buckets

# Удалить bucket
python main.py rb my-bucket
```

### 4. Настроить пользователей (домашнее задание, часть 2)

```bash
python setup_users.py
```

Это создаст:
- `bucket1`, `bucket2`
- `user1` — чтение в `bucket1`, чтение+запись в `bucket2`
- `user2` — чтение в `bucket2`

---

## Переменные окружения

| Переменная     | По умолчанию            | Описание           |
|----------------|-------------------------|--------------------|
| `S3_ENDPOINT`  | `http://localhost:9000` | URL S3 хранилища   |
| `S3_ACCESS_KEY`| `minioadmin`            | Access Key         |
| `S3_SECRET_KEY`| `minioadmin`            | Secret Key         |
| `S3_REGION`    | `us-east-1`             | Регион             |

CLI-флаги `--endpoint`, `--access-key`, `--secret-key`, `--region` перекрывают переменные окружения.

### Пример подключения от user1

```bash
S3_ACCESS_KEY=user1 S3_SECRET_KEY=User1Password! python main.py ls bucket1
```

---

## Политики доступа (IAM)

### user1

```json
// read-bucket1: чтение в bucket1
{
  "Effect": "Allow",
  "Action": ["s3:GetBucketLocation", "s3:ListBucket", "s3:GetObject"],
  "Resource": ["arn:aws:s3:::bucket1", "arn:aws:s3:::bucket1/*"]
}

// readwrite-bucket2: чтение+запись в bucket2
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", ...],
  "Resource": ["arn:aws:s3:::bucket2/*"]
}
```

### user2

```json
// read-bucket2: только чтение в bucket2
{
  "Effect": "Allow",
  "Action": ["s3:GetBucketLocation", "s3:ListBucket", "s3:GetObject"],
  "Resource": ["arn:aws:s3:::bucket2", "arn:aws:s3:::bucket2/*"]
}
```