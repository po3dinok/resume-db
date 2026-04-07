# Resume DB Tools

CLI утилиты для работы с базой резюме кандидатов.

## Возможности

- Парсинг PDF резюме (hh.ru формат)
- Поиск по базе SQLite
- Анализ и фильтрация кандидатов
- Импорт данных

## Установка

```bash
pip install -r requirements.txt
```

## Использование

```bash
python pdf_parser.py ./pdfs/
python pdf_parser.py ./pdfs/ --json
```

## Требования

- Python 3.10+
- pypdf
