#!/usr/bin/env python3
"""
Тест работы с фильтрами zakupki.gov.ru
"""

import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.zakupki_filters import ZakupkiFilters
from app.services.parsers.zakupki import ZakupkiParser


def test_filters():
    """Тестирует создание URL с различными фильтрами"""
    
    print("=== Тест фильтров zakupki.gov.ru ===\n")
    
    # Базовый URL без фильтров
    filters = ZakupkiFilters()
    print("1. Базовый URL:")
    print(filters.build_url())
    print()
    
    # URL с поисковым запросом
    filters = ZakupkiFilters()
    filters.set_search_text("медицинское оборудование")
    print("2. Поиск по тексту:")
    print(filters.build_url())
    print()
    
    # URL с сортировкой по цене
    filters = ZakupkiFilters()
    filters.set_sort("PRICE", ascending=False)  # По убыванию цены
    print("3. Сортировка по цене (убывание):")
    print(filters.build_url())
    print()
    
    # URL с пагинацией
    filters = ZakupkiFilters()
    filters.set_page(3).set_records_per_page(50)
    print("4. Страница 3, по 50 записей:")
    print(filters.build_url())
    print()
    
    # URL только с 44-ФЗ
    filters = ZakupkiFilters()
    filters.set_law_types(fz44=True, fz223=False, af=False)
    print("5. Только 44-ФЗ:")
    print(filters.build_url())
    print()
    
    # URL с диапазоном цен
    filters = ZakupkiFilters()
    filters.set_price_range(min_price=100000, max_price=1000000)
    print("6. Цена от 100,000 до 1,000,000:")
    print(filters.build_url())
    print()
    
    # URL с диапазоном дат
    filters = ZakupkiFilters()
    filters.set_date_range(date_from="01.01.2026", date_to="31.12.2026")
    print("7. Даты с 01.01.2026 по 31.12.2026:")
    print(filters.build_url())
    print()
    
    # Комплексный фильтр
    filters = ZakupkiFilters()
    filters.set_search_text("строительство").set_sort("PRICE", False).set_page(2).set_records_per_page(20).set_law_types(fz44=True, fz223=True, af=False).set_price_range(500000, 5000000)
    print("8. Комплексный фильтр:")
    print(filters.build_url())
    print()


def test_parser_with_filters():
    """Тестирует создание URL через парсер"""
    
    print("=== Тест парсера с фильтрами ===\n")
    
    parser = ZakupkiParser()
    
    # Простой поиск
    url1 = parser.create_filtered_url(search_text="компьютеры")
    print("1. Поиск компьютеров:")
    print(url1)
    print()
    
    # Сложный фильтр
    url2 = parser.create_filtered_url(
        search_text="мебель",
        sort_by="PRICE",
        ascending=True,
        page=1,
        records_per_page=20,
        law_types={"fz44": True, "fz223": False, "af": False},
        price_range={"min": 50000, "max": 500000},
        date_range={"from": "01.01.2026", "to": "31.01.2026"}
    )
    print("2. Сложный фильтр:")
    print(url2)
    print()


def test_url_parsing():
    """Тестирует парсинг URL обратно в фильтры"""
    
    print("=== Тест парсинга URL ===\n")
    
    # Исходный URL
    original_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&searchString=test&sortBy=PRICE&sortDirection=true&pageNumber=2"
    print("Исходный URL:")
    print(original_url)
    print()
    
    # Парсим URL
    filters = ZakupkiFilters.from_url(original_url)
    print("Извлеченные фильтры:")
    for key, value in filters.get_filters_dict().items():
        print(f"  {key}: {value}")
    print()
    
    # Строим URL обратно
    rebuilt_url = filters.build_url()
    print("Восстановленный URL:")
    print(rebuilt_url)
    print()


if __name__ == "__main__":
    test_filters()
    test_parser_with_filters()
    test_url_parsing()
    
    print("Все тесты фильтров выполнены успешно!")