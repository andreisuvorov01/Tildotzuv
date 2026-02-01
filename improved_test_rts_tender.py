#!/usr/bin/env python3
"""
Улучшенный тест для проверки работы парсера RTS Tender с обновленной логикой
"""

import sys
import os
import asyncio

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.parsers.rts_tender import RtsTenderParser


def test_improved_parser_logic():
    """Тестирует улучшенную логику парсера"""
    
    print("=== Тест улучшенной логики парсера RTS Tender ===\n")
    
    # Создаем парсер
    parser = RtsTenderParser()
    
    # Тестовые HTML-страницы
    html_with_real_content = """
    <html>
    <head><title>Закупки на RTS Tender</title></head>
    <body>
        <div class="tender-item">
            <div class="tender-name">Поставка компьютерного оборудования</div>
            <div class="customer-name">ООО Ромашка</div>
            <div class="tender-price">2 500 000 руб.</div>
        </div>
        <div class="tender-item">
            <div class="tender-name">Ремонт офисных помещений</div>
            <div class="customer-name">АО Звезда</div>
            <div class="tender-price">10 000 000 руб.</div>
        </div>
    </body>
    </html>
    """
    
    html_with_procurements_indicators = """
    <html>
    <head><title>Результаты поиска тендеров</title></head>
    <body>
        <h1>Результаты поиска тендеров и закупок</h1>
        <p>Найдено 456 лотов</p>
        <div class="search-results">
            <div class="tender-card">
                <span>Тендер на поставку товаров</span>
                <span>Процедура №12345</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_with_content_but_no_specific_selectors = """
    <html>
    <head><title>RTS Tender - Закупки</title></head>
    <body>
        <div class="lots-container">
            <div class="lot">
                <h3>Наименование лота: Поставка канцелярии</h3>
                <p>Заказчик: ООО Луч</p>
                <p>Начальная цена: 500 000 рублей</p>
            </div>
            <div class="lot">
                <h3>Наименование лота: Услуги по уборке</h3>
                <p>Заказчик: ИП Петров</p>
                <p>Начальная цена: 1 200 000 рублей</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_without_procurement_indicators = """
    <html>
    <head><title>Главная страница</title></head>
    <body>
        <h1>Добро пожаловать на RTS-Tender</h1>
        <p>Это главная страница сайта</p>
        <div class="navigation">
            <a href="/tenders">Тендеры</a>
            <a href="/auctions">Аукционы</a>
        </div>
    </body>
    </html>
    """
    
    test_cases = [
        ("Страница с реальным контентом тендеров", html_with_real_content),
        ("Страница с индикаторами закупок", html_with_procurements_indicators),
        ("Страница с контентом, но другими селекторами", html_with_content_but_no_specific_selectors),
        ("Страница без индикаторов закупок", html_without_procurement_indicators),
    ]
    
    for description, html in test_cases:
        print(f"Тест: {description}")
        results = parser.parse(html, "https://www.rts-tender.ru/auctions")
        
        if results:
            print(f"  Найдено результатов: {len(results)}")
            if len(results) > 0:
                first_result = results[0]
                print(f"  Первый результат: {first_result.text[:60]}...")
                print(f"  Автор: {first_result.author}")
                print(f"  Рейтинг/цена: {first_result.rating}")
                
                # Проверяем тип результата
                if "не удалось извлечь данные" in first_result.text:
                    print("  ❌ Результат: Ошибка извлечения данных")
                elif "Обнаружены признаки закупок" in first_result.text:
                    print("  ⚠️  Результат: Обнаружены признаки, но нет данных")
                elif "Закупки не найдены" in first_result.text:
                    print("  ❌ Результат: Закупки не найдены")
                else:
                    print("  ✅ Результат: Успешное извлечение данных")
        else:
            print("  Результат: Нет данных для парсинга")
        print()


def test_cloudflare_bypass_scenarios():
    """Тестирует сценарии обхода Cloudflare"""
    
    print("=== Тест сценариев обхода Cloudflare ===\n")
    
    parser = RtsTenderParser()
    
    # HTML после частичного обхода Cloudflare
    html_after_partial_bypass = """
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <div id="cf-browser-verification">
            <h1>Checking your browser</h1>
            <p>Anti-DDoS защита активна</p>
        </div>
        <script>/* Cloudflare challenge scripts */</script>
    </body>
    </html>
    """
    
    # HTML с контентом, но после защиты
    html_with_content_after_protection = """
    <html>
    <head><title>RTS Tender - Результаты поиска</title></head>
    <body>
        <h1>Поиск тендеров</h1>
        <p>По вашему запросу найдено 23 тендера</p>
        <div class="tender-item">
            <div class="tender-name">Тендер на поставку материалов</div>
            <div class="customer">ООО СтройИнвест</div>
            <div class="price">7 500 000 руб.</div>
        </div>
    </body>
    </html>
    """
    
    scenarios = [
        ("Страница с активной защитой Cloudflare", html_after_partial_bypass),
        ("Страница с контентом после защиты", html_with_content_after_protection),
    ]
    
    for description, html in scenarios:
        print(f"Сценарий: {description}")
        results = parser.parse(html, "https://www.rts-tender.ru/auctions")
        
        if results:
            print(f"  Результат обработки: {results[0].text[:60]}...")
        else:
            print("  Результат: Нет данных")
        print()


if __name__ == "__main__":
    test_improved_parser_logic()
    test_cloudflare_bypass_scenarios()
    print("=== Тесты завершены ===")