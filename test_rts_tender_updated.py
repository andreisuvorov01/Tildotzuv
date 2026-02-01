#!/usr/bin/env python3
"""
Тест для проверки работы парсера RTS Tender с обновленной логикой
"""

import sys
import os
import asyncio

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.parsers.rts_tender import RtsTenderParser


def test_cloudflare_detection():
    """Тестирует обнаружение Cloudflare защиты"""
    
    print("=== Тест обнаружения Cloudflare защиты ===\n")
    
    # Создаем парсер
    parser = RtsTenderParser()
    
    # Тестовые HTML-страницы
    html_with_protection = """
    <html>
    <head><title>Checking your browser</title></head>
    <body>
    <div id="cf-browser-verification">Anti-DDoS защита</div>
    <p>Checking your browser before accessing rts-tender.ru.</p>
    </body>
    </html>
    """
    
    html_without_protection = """
    <html>
    <head><title>RTS Tender - Закупки</title></head>
    <body>
    <div class="tender-item">
        <div class="tender-name">Поставка офисной мебели</div>
        <div class="customer-name">Газпром нефть</div>
        <div class="tender-price">1 200 000 руб.</div>
    </div>
    <div class="tender-item">
        <div class="tender-name">Ремонт зданий</div>
        <div class="customer-name">Роснефть</div>
        <div class="tender-price">5 000 000 руб.</div>
    </div>
    </body>
    </html>
    """
    
    html_with_cloudflare_but_content = """
    <html>
    <head><title>Закупки на RTS Tender</title></head>
    <body>
    <!-- Cloudflare script tags would be here in real content -->
    <div class="tender-item">
        <div class="tender-name">Поставка компьютерного оборудования</div>
        <div class="customer-name">Лукойл</div>
        <div class="tender-price">2 500 000 руб.</div>
    </div>
    </body>
    </html>
    """
    
    test_cases = [
        ("Страница с защитой Cloudflare", html_with_protection),
        ("Страница с контентом без защиты", html_without_protection),
        ("Страница с контентом за Cloudflare", html_with_cloudflare_but_content),
    ]
    
    for description, html in test_cases:
        print(f"Тест: {description}")
        results = parser.parse(html, "https://www.rts-tender.ru/auctions")
        
        if results:
            print(f"  Найдено результатов: {len(results)}")
            if results[0].text == "РТС-тендер защищен Cloudflare Anti-DDoS. Требуется обход защиты.":
                print("  Результат: Обнаружена защита Cloudflare (ожидаемо)")
            else:
                print(f"  Первый результат: {results[0].text[:50]}...")
        else:
            print("  Результат: Нет данных для парсинга (ожидаемо для URL)")
        print()


if __name__ == "__main__":
    test_cloudflare_detection()
    print("=== Тест завершен ===")