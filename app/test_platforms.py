#!/usr/bin/env python3
"""
Тест доступности площадок для закупок
"""
import requests

def test_platforms():
    """Тестируем доступность различных площадок"""

    platforms = {
        'zakupki.gov.ru': 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html',
        'Росэлторг': 'https://www.roseltorg.ru/procedures',
        'РТС-тендер': 'https://www.rts-tender.ru/auction',
        'Сбербанк-АСТ': 'https://www.sberbank-ast.ru/purchaseList.aspx',
        'НЭП': 'https://neptek.ru/trades'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    print("=== Testing platform accessibility ===\n")

    for name, url in platforms.items():
        try:
            print(f"Testing {name}: {url}")
            response = requests.head(url, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"✅ {name}: OK (status {response.status_code})")
            elif response.status_code == 403:
                print(f"⚠️ {name}: Blocked (status {response.status_code})")
            elif response.status_code == 404:
                print(f"⚠️ {name}: Not found (status {response.status_code})")
            else:
                print(f"❓ {name}: Unknown status {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Failed - {str(e)[:50]}...")

        print()

if __name__ == "__main__":
    test_platforms()

