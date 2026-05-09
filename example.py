import os
from dotenv import load_dotenv
from cloudflare_api import CloudflareBrowserRendering
import json
import time

# Загрузка переменных окружения
load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

def example_crawl():
    if not ACCOUNT_ID or not API_TOKEN:
        print("Ошибка: Укажите CLOUDFLARE_ACCOUNT_ID и CLOUDFLARE_API_TOKEN в .env")
        return

    cf = CloudflareBrowserRendering(ACCOUNT_ID, API_TOKEN)

    print("--- Пример использования /crawl ---")
    start_url = "https://example.com"

    # Запуск краулинга
    try:
        init_res = cf.start_crawl(start_url, limit=5, formats=["markdown"])
        if init_res.get("success"):
            job_id = init_res["result"]
            print(f"Задача запущена. Job ID: {job_id}")

            # Поллинг результатов
            while True:
                status_res = cf.get_crawl_results(job_id, params={"limit": 1})
                status = status_res["result"]["status"]
                print(f"Статус: {status}")

                if status == "completed":
                    full_results = cf.get_crawl_results(job_id)
                    print(f"Краулинг завершен. Найдено страниц: {full_results['result']['total']}")
                    break
                elif status in ["errored", "cancelled_due_to_timeout", "cancelled_due_to_limits"]:
                    print(f"Краулинг прерван со статусом: {status}")
                    break

                time.sleep(5)
    except Exception as e:
        print(f"Произошла ошибка при краулинге: {e}")

def example_json_extraction():
    if not ACCOUNT_ID or not API_TOKEN:
        return

    cf = CloudflareBrowserRendering(ACCOUNT_ID, API_TOKEN)

    print("\n--- Пример использования /json (извлечение отзывов) ---")
    url = "https://example.com/reviews" # Гипотетический URL

    prompt = "Extract user reviews from this page. For each review, get the author name, rating, and the review text."
    schema = {
        "type": "object",
        "properties": {
            "reviews": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "author": {"type": "string"},
                        "rating": {"type": "number"},
                        "text": {"type": "string"}
                    },
                    "required": ["author", "text"]
                }
            }
        }
    }

    try:
        # В реальности этот вызов может упасть, если URL недоступен или ключи неверны
        # Но логика вызова API верна
        res = cf.extract_json(url, prompt=prompt, response_format={"type": "json_schema", "schema": schema})
        print(json.dumps(res, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка при извлечении JSON: {e} (это ожидаемо без реальных ключей)")

if __name__ == "__main__":
    # example_crawl()
    example_json_extraction()
