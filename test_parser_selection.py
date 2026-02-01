#!/usr/bin/env python3
"""
Тест автоматического выбора парсера для разных URL
"""

import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper_engine import ScraperEngine


def test_parser_selection():
    """Тестирует автоматический выбор парсера для разных URL"""
    
    engine = ScraperEngine()
    
    test_urls = [
        ("https://avito.ru/moskva/kvartiry", "AvitoParser"),
        ("https://m.avito.ru/moskva/kvartiry", "AvitoParser"),
        ("https://zakupki.gov.ru/epz/order/extendedsearch/results.html", "ZakupkiParser"),
        ("https://www.zakupki.gov.ru/epz/order/extendedsearch/results.html", "ZakupkiParser"),
        ("https://example.com", "AvitoParser"),  # Fallback к первому парсеру
    ]
    
    print("=== Тест автоматического выбора парсера ===\n")
    
    all_passed = True
    
    for url, expected_parser in test_urls:
        scraper = engine._get_scraper(url)
        actual_parser = scraper.__class__.__name__
        
        status = "✓" if actual_parser == expected_parser else "✗"
        print(f"{status} URL: {url}")
        print(f"  Ожидаемый парсер: {expected_parser}")
        print(f"  Выбранный парсер: {actual_parser}")
        
        if actual_parser != expected_parser:
            all_passed = False
        
        print()
    
    if all_passed:
        print("Все тесты прошли успешно!")
        return True
    else:
        print("Некоторые тесты провалились!")
        return False


def test_zakupki_domain_check():
    """Тестирует метод should_handle для ZakupkiParser"""
    
    from app.services.parsers.zakupki import ZakupkiParser
    
    parser = ZakupkiParser()
    
    test_cases = [
        ("https://zakupki.gov.ru/epz/order/extendedsearch/results.html", True),
        ("https://www.zakupki.gov.ru/epz/order/extendedsearch/results.html", True),
        ("http://zakupki.gov.ru/epz/order/extendedsearch/results.html", True),
        ("https://avito.ru/moskva/kvartiry", False),
        ("https://example.com", False),
    ]
    
    print("=== Тест метода should_handle для ZakupkiParser ===\n")
    
    all_passed = True
    
    for url, expected in test_cases:
        result = parser.should_handle(url)
        status = "✓" if result == expected else "✗"
        
        print(f"{status} URL: {url}")
        print(f"  Ожидаемый результат: {expected}")
        print(f"  Фактический результат: {result}")
        print()
        
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("Все тесты should_handle прошли успешно!")
        return True
    else:
        print("Некоторые тесты should_handle провалились!")
        return False


if __name__ == "__main__":
    print("Запуск тестов парсера zakupki.gov.ru...\n")
    
    test1_passed = test_parser_selection()
    test2_passed = test_zakupki_domain_check()
    
    print("\n" + "="*50)
    if test1_passed and test2_passed:
        print("Все тесты прошли успешно! Парсер zakupki.gov.ru готов к использованию.")
    else:
        print("Некоторые тесты провалились. Проверьте конфигурацию парсера.")