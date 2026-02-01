#!/usr/bin/env python3
"""
Простой тест браузера
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.core.browser import browser_manager

async def test_browser():
    try:
        await browser_manager.startup()
        print("Browser started successfully")

        context = await browser_manager.get_context()
        page = await browser_manager.new_page(context)

        # Простой тест
        await page.goto("https://httpbin.org/ip", timeout=10000)
        content = await page.content()
        print("Page loaded successfully")

        await page.close()
        await context.close()

        await browser_manager.shutdown()
        print("Browser test completed successfully")

    except Exception as e:
        print(f"Browser test failed: {e}")
        await browser_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(test_browser())
