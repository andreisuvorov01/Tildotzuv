#!/usr/bin/env python3
"""
Тест прокси через Playwright
"""
import asyncio
from patchright.async_api import async_playwright
try:
    from playwright_stealth import stealth_async
except ImportError:
    stealth_async = None

async def test_proxy_playwright():
    """Тестирует прокси через Playwright"""

    # Тестируем HTTP прокси
    proxy_config = {
        "server": "http://176.9.113.112:48000",
        "username": "494300202",
        "password": "5hrIZjjYavY4ZmOQlKIm"
    }

    print(f"Testing proxy via Playwright: {proxy_config}")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                proxy=proxy_config,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )

            context = await browser.new_context()
            page = await context.new_page()
            if stealth_async:
                await stealth_async(page)

            # Test 1: Check IP
            print("1. Checking IP...")
            try:
                await page.goto("http://httpbin.org/ip", timeout=15000)
                content = await page.content()
                if "origin" in content:
                    print("OK: IP test passed!")
                else:
                    print("ERROR: Could not get IP")
            except Exception as e:
                print(f"ERROR: IP check failed: {e}")

            # Test 2: Access zakupki.gov.ru
            print("2. Testing zakupki.gov.ru...")
            try:
                response = await page.goto("https://zakupki.gov.ru", timeout=15000)
                print(f"OK: Response status: {response.status}")
                if response.status == 200:
                    print("OK: zakupki.gov.ru accessible!")
                else:
                    print(f"WARN: Unexpected status: {response.status}")
            except Exception as e:
                print(f"ERROR: zakupki.gov.ru access failed: {e}")

            await browser.close()

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_proxy_playwright())
