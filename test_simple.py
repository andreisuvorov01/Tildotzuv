#!/usr/bin/env python3
"""
Упрощенный тест парсера zakupki.gov.ru без зависимостей
"""

import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.parsers.zakupki import ZakupkiParser
from app.services.parsers.avito import AvitoParser


def test_parser_domain_detection():
    """Тестирует определение домена для парсеров"""
    
    zakupki_parser = ZakupkiParser()
    avito_parser = AvitoParser()
    
    test_cases = [
        # (URL, ожидаемый парсер)
        ("https://zakupki.gov.ru/epz/order/extendedsearch/results.html", "ZakupkiParser"),
        ("https://www.zakupki.gov.ru/epz/order/extendedsearch/results.html", "ZakupkiParser"),
        ("http://zakupki.gov.ru/epz/order/extendedsearch/results.html", "ZakupkiParser"),
        ("https://avito.ru/moskva/kvartiry", "AvitoParser"),
        ("https://m.avito.ru/moskva/kvartiry", "AvitoParser"),
        ("https://www.avito.ru/moskva/kvartiry", "AvitoParser"),
    ]
    
    print("=== Тест определения домена парсерами ===\n")
    
    all_passed = True
    
    for url, expected_parser in test_cases:
        zakupki_handles = zakupki_parser.should_handle(url)
        avito_handles = avito_parser.should_handle(url)
        
        if expected_parser == "ZakupkiParser":
            expected_zakupki = True
            expected_avito = False
        else:
            expected_zakupki = False
            expected_avito = True
        
        zakupki_ok = zakupki_handles == expected_zakupki
        avito_ok = avito_handles == expected_avito
        
        status = "OK" if (zakupki_ok and avito_ok) else "FAIL"
        
        print(f"{status} URL: {url}")
        print(f"  Ожидаемый парсер: {expected_parser}")
        print(f"  ZakupkiParser.should_handle(): {zakupki_handles} (ожидалось: {expected_zakupki})")
        print(f"  AvitoParser.should_handle(): {avito_handles} (ожидалось: {expected_avito})")
        print()
        
        if not (zakupki_ok and avito_ok):
            all_passed = False
    
    return all_passed


def test_zakupki_parser_structure():
    """Тестирует структуру ZakupkiParser"""
    
    print("=== Тест структуры ZakupkiParser ===\n")
    
    parser = ZakupkiParser()
    
    # Проверяем наличие необходимых атрибутов
    checks = [
        ("domain", hasattr(parser, 'domain')),
        ("selectors", hasattr(parser, 'selectors')),
        ("parse method", hasattr(parser, 'parse')),
        ("should_handle method", hasattr(parser, 'should_handle')),
    ]
    
    all_passed = True
    
    for check_name, result in checks:
        status = "OK" if result else "FAIL"
        print(f"{status} {check_name}: {'OK' if result else 'MISSING'}")
        
        if not result:
            all_passed = False
    
    # Проверяем значения
    if hasattr(parser, 'domain'):
        domain_ok = parser.domain == "zakupki.gov.ru"
        status = "OK" if domain_ok else "FAIL"
        print(f"{status} domain value: '{parser.domain}' {'OK' if domain_ok else 'WRONG'}")
        if not domain_ok:
            all_passed = False
    
    if hasattr(parser, 'selectors'):
        required_selectors = ['container', 'text', 'author', 'rating']
        for selector in required_selectors:
            has_selector = selector in parser.selectors
            status = "OK" if has_selector else "FAIL"
            print(f"{status} selector '{selector}': {'OK' if has_selector else 'MISSING'}")
            if not has_selector:
                all_passed = False
    
    print()
    return all_passed


if __name__ == "__main__":
    print("Запуск упрощенных тестов парсера zakupki.gov.ru...\n")
    
    test1_passed = test_parser_domain_detection()
    test2_passed = test_zakupki_parser_structure()
    
    print("="*60)
    if test1_passed and test2_passed:
        print("[OK] Все тесты прошли успешно!")
        print("[OK] Парсер zakupki.gov.ru корректно интегрирован в проект.")
        print("[OK] Готов к использованию через API.")
    else:
        print("[FAIL] Некоторые тесты провалились.")
        print("[FAIL] Проверьте конфигурацию парсера.")