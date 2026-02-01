#!/usr/bin/env python3
"""
Тест парсинга zakupki.gov.ru без прокси
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.browser import browser_manager
from app.services.parsers.zakupki import ZakupkiParser

async def test_zakupki_no_proxy():
    """Тестирует zakupki.gov.ru без прокси"""

    url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&ppRf615=on&af=on&currencyIdGeneral=-1"

    print(f"Testing zakupki.gov.ru without proxy: {url}")

    try:
        # Запускаем браузер
        await browser_manager.startup()

        # Создаем контекст без аккаунта (без прокси)
        context = await browser_manager.get_context(None)
        page = await browser_manager.new_page(context)

        # Устанавливаем таймаут
        page.set_default_timeout(120000)

        # Добавляем заголовки
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

        print("Loading page...")
        await page.goto(url, wait_until="domcontentloaded", timeout=120000)
        print("Page loaded successfully!")

        # Ждем немного для загрузки динамического контента
        await asyncio.sleep(3)

        # Получаем HTML
        html = await page.content()
        print(f"HTML length: {len(html)} characters")

        # Делаем скриншот
        await page.screenshot(path="test_zakupki_no_proxy.png")

        # Парсим
        parser = ZakupkiParser()
        results = parser.parse(html, url)

        print(f"Parsed {len(results)} items:")
        for i, item in enumerate(results[:3], 1):
            print(f"{i}. {item.text[:100]}...")

        await page.close()
        await context.close()
        await browser_manager.shutdown()

        print("Test completed successfully!")

    except Exception as e:
        print(f"Test failed: {e}")
        await browser_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(test_zakupki_no_proxy())
