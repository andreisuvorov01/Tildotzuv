import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# Ваши данные прокси
PROXY_URL = "socks5://494300202:5hrIZjjYavY4ZmOQlKIm@176.9.113.112:48001"  # SOCKS5


async def test_proxy():
    print(f"🐢 Проверяем прокси: {PROXY_URL}")

    # Парсим URL прокси
    parsed = urlparse(PROXY_URL)

    # Формируем конфигурацию для Playwright
    proxy_config = {
        "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
    }

    # Добавляем аутентификацию если есть
    if parsed.username and parsed.password:
        proxy_config["username"] = parsed.username
        proxy_config["password"] = parsed.password

    async with async_playwright() as p:
        try:
            # Запускаем браузер с SOCKS5 прокси
            browser = await p.chromium.launch(
                headless=False,
                proxy=proxy_config
            )
            page = await browser.new_page()

            # ТЕСТ 1: Доступ в интернет (Узнаем IP)
            print("1️⃣ Идем на ifconfig.me (проверка IP)...")
            try:
                await page.goto("http://ifconfig.me", timeout=30000)
                ip = await page.inner_text("body")
                print(f"✅ Успех! Ваш внешний IP: {ip}")
            except Exception as e:
                print(f"❌ Не удалось соединиться с сайтом проверки IP. Прокси не работает.\nОшибка: {e}")
                await browser.close()
                return

            # ТЕСТ 2: Доступ к Авито
            print("\n2️⃣ Пробуем открыть Avito...")
            try:
                response = await page.goto("https://m.avito.ru", timeout=30000)
                print(f"Статус ответа: {response.status}")

                if "Доступ ограничен" in await page.content():
                    print("⛔ БАН! Прокси работает, но Авито заблокировал этот IP.")
                else:
                    print("✅ Авито открылся! Прокси подходит.")

            except Exception as e:
                print(f"❌ Ошибка при открытии Авито (таймаут или срыв): {e}")

            await asyncio.sleep(5)  # Даем время посмотреть
            await browser.close()

        except Exception as e:
            print(f"💀 Критическая ошибка браузера: {e}")


if __name__ == "__main__":
    asyncio.run(test_proxy())