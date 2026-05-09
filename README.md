# Tildotzuv
Сервис по интеграции парсера отзывов в тильду.

## Интеграция с Cloudflare Browser Rendering

Проект поддерживает новые возможности Cloudflare Browser Rendering для эффективного парсинга сайтов:
1. **Эндпоинт `/crawl`**: Позволяет обходить целые сайты (до 100,000 страниц) за один вызов. Поддерживает форматы HTML, Markdown и структурированный JSON.
2. **Эндпоинт `/json`**: Использует AI (по умолчанию Llama 3.3) для извлечения структурированных данных из веб-страниц по текстовому запросу (промпту) или JSON-схеме.

### Настройка
1. Скопируйте файл `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```
2. Укажите ваши `CLOUDFLARE_ACCOUNT_ID` и `CLOUDFLARE_API_TOKEN` (токен должен иметь права `Browser Rendering: Edit`).
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

### Использование
Для работы с API используйте класс `CloudflareBrowserRendering` из модуля `cloudflare_api.py`.

Пример извлечения отзывов:
```python
from cloudflare_api import CloudflareBrowserRendering

cf = CloudflareBrowserRendering(ACCOUNT_ID, API_TOKEN)
res = cf.extract_json(
    url="https://example.com/reviews",
    prompt="Extract reviews with author and text",
    response_format={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "reviews": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "author": {"type": "string"},
                            "text": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)
print(res["result"]["reviews"])
```

Подробный пример работы с краулером доступен в `example.py`.
