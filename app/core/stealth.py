"""
Модуль для реализации методов обхода антибот-защиты
"""
import asyncio
import random
import time
from typing import Dict, Optional

def enhance_stealth(context_or_page):
    """
    Применяет методы обхода обнаружения ботов к контексту или странице Playwright
    """
    # Удаление следов автоматизации
    context_or_page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Скрытие следов headless режима
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ru-RU', 'ru', 'en-US', 'en'],
        });
        
        // WebGL spoofing
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Google Inc.';
            if (parameter === 37446) return 'ANGLE (Google, Vulkan 1.0.0, SwiftShader Device (Subzero, Hana))';
            return getParameter(parameter);
        };
        
        // Canvas spoofing
        const ctx = document.createElement('canvas').getContext('2d');
        const fillText = ctx.fillText;
        ctx.fillText = function(...args) {
            args[0] = args[0].split('').reverse().join('');
            return fillText.apply(this, args);
        };
    """)
    
    return context_or_page

def apply_nodriver_stealth(browser):
    """
    Применяет методы обхода обнаружения для nodriver
    """
    # nodriver сам по себе уже обходит большинство проверок
    # но можно дополнительно настроить параметры
    pass

async def simulate_human_behavior(page):
    """
    Имитирует человеческое поведение на странице
    """
    # Случайная задержка перед действиями
    await asyncio.sleep(random.uniform(1, 3))
    
    # Имитация движения мыши
    viewport = await page.viewport_size()
    await page.mouse.move(
        random.randint(100, viewport['width'] - 100),
        random.randint(100, viewport['height'] - 100)
    )
    
    # Случайная прокрутка
    await page.mouse.wheel(0, random.randint(200, 800))
    
    # Случайная задержка
    await asyncio.sleep(random.uniform(0.5, 2))

def create_tls_fingerprinting_headers():
    """
    Создает заголовки, имитирующие реальный браузер для обхода TLS fingerprinting
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    return headers

def get_random_user_agent():
    """
    Возвращает случайный User-Agent для имитации разных браузеров
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

def simulate_cookie_sharing():
    """
    Симуляция использования куки cf_clearance между сессиями
    """
    # В реальном приложении здесь будет логика сохранения и повторного использования cf_clearance
    pass

def seleniumbase_stealth_options():
    """
    Возвращает опции для SeleniumBase UC Mode с встроенными методами обхода
    """
    options = {
        'uc': True,  # Включаем UC Mode
        'headless': True,
        'incognito': False,
        'disable_gpu': True,
        'locale_code': 'ru',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    return options

def patchright_stealth_options():
    """
    Возвращает опции для Patchright с улучшенной защитой от детекции CDP
    """
    options = [
        "--no-sandbox",
        "--disable-dev-shm-usage", 
        "--disable-blink-features=AutomationControlled",
        "--window-size=1920,1080",
        "--disable-features=VizDisplayCompositor",
        "--disable-ipc-flooding-protection"
    ]
    return options

def drissionpage_stealth_options():
    """
    Возвращает опции для DrissionPage с комбинированным подходом
    """
    options = {
        'addr_or_opts': "--remote-debugging-port=9222 --no-first-run --disable-blink-features=AutomationControlled --window-size=1920,1080"
    }
    return options
