#!/usr/bin/env python3
"""
Тест с использованием requests вместо Playwright
"""
import requests
from app.services.parsers.zakupki import ZakupkiParser

def test_requests():
    """Тестируем парсинг с requests"""

    url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&ppRf615=on&af=on&currencyIdGeneral=-1"

    print(f"Testing with requests: {url}")

    try:
        # Используем тот же подход что и в network.py
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
            },
            timeout=30
        )

        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")

        if response.status_code == 200:
            parser = ZakupkiParser()
            results = parser.parse(response.text, url)
            print(f"Parsed {len(results)} items")
            return True
        else:
            print(f"Bad status: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_requests()
    print(f"Test {'PASSED' if success else 'FAILED'}")
