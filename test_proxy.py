import asyncio
import os
from app.core.browser import browser_manager

async def test_proxy():
    """Тест проверки работы прокси"""
    
    # Устанавливаем прокси
    os.environ['PROXY_URL'] = 'http://494300202:5hrIZjjYavY4ZmOQlKIm@176.9.113.112:48000'
    os.environ['HEADLESS'] = 'false'  # Показываем браузер для наглядности
    
    try:
        await browser_manager.startup()
        context = await browser_manager.get_context()
        page = await browser_manager.new_page(context)
        
        # Проверяем IP через сервис
        print("Проверяем IP через прокси...")
        await page.goto("https://httpbin.org/ip", timeout=30000)
        
        # Получаем содержимое страницы
        content = await page.content()
        print("Ответ от httpbin.org/ip:")
        print(content)
        
        # Проверяем доступность Avito
        print("\nПроверяем доступность Avito...")
        await page.goto("https://m.avito.ru", timeout=30000)
        title = await page.title()
        print(f"Заголовок страницы Avito: {title}")
        
        await page.close()
        await context.close()
        
        print("✅ Прокси работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании прокси: {e}")
    finally:
        await browser_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(test_proxy())