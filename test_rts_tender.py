#!/usr/bin/env python3
"""
Тест для проверки работы парсера RTS Tender
"""

import sys
import os
import asyncio

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper_engine import ScraperEngine
from app.services.parsers.rts_tender import RtsTenderParser


async def test_rts_tender_parser():
    """Тестирует парсер RTS Tender"""
    
    print("=== Тест парсера RTS Tender ===\n")
    
    # Создаем парсер
    parser = RtsTenderParser()
    
    # Тестируем метод should_handle
    test_urls = [
        "https://www.rts-tender.ru/auctions",
        "https://rts-tender.ru/poisk/poisk-44-fz?keywords=test",
        "https://example.com"
    ]
    
    print("1. Тест метода should_handle:")
    for url in test_urls:
        result = parser.should_handle(url)
        print(f"   URL: {url}")
        print(f"   Результат: {result}")
        print()
    
    # Тестируем метод create_filtered_url
    print("2. Тест метода create_filtered_url:")
    filtered_url = parser.create_filtered_url(search_text="тест", records_per_page=10)
    print(f"   Отфильтрованный URL: {filtered_url}")
    print()
    
    # Тестируем интеграцию с scraper engine
    print("3. Тест интеграции с scraper engine:")
    engine = ScraperEngine()
    
    # Используем тестовый URL
    test_url = "https://www.rts-tender.ru/auctions"
    
    try:
        print(f"   Запуск парсинга для URL: {test_url}")
        results = await engine.run(test_url)
        print(f"   Получено результатов: {len(results)}")
        
        if results:
            print("   Первый результат:")
            print(f"     Текст: {results[0].text[:100]}...")
            print(f"     Автор: {results[0].author}")
            print(f"     Рейтинг: {results[0].rating}")
        else:
            print("   Результаты не получены")
            
    except Exception as e:
        print(f"   Ошибка при парсинге: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Тест завершен ===")


if __name__ == "__main__":
    asyncio.run(test_rts_tender_parser())