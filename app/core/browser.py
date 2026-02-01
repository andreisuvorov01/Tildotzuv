import asyncio
import logging
from typing import Optional, Dict, Any
import nodriver as uc
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.core.stealth import enhance_stealth, apply_nodriver_stealth, simulate_human_behavior
from app.core.accounts import account_manager

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.contexts = {}  # Контексты для разных аккаунтов
        
    async def startup(self):
        """Инициализация Playwright"""
        self.playwright = await async_playwright().start()
    async def shutdown(self):
        """Завершение работы Playwright"""
        for context in self.contexts.values():
            await context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def set_session_id(self, session_id: str):
        """Установка ID сессии для менеджера браузера"""
        # This method can be used to associate the browser manager with a specific session
        # For now, we'll just store the session ID as an attribute
        self.session_id = session_id
    
    async def get_context(self, account: Optional[Dict] = None) -> BrowserContext:
        """Получение браузерного контекста с учетом аккаунта"""
        if not self.browser:
            # Запуск браузера с оптимальными аргументами
            launch_options = {
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-images",  # Для скорости
                    "--disable-javascript",  # Может быть включен позже при необходимости
                    "--no-first-run",
                    "--disable-default-apps",
                    "--disable-sync",
                    "--disable-translate",
                    "--hide-scrollbars",
                    "--metrics-recording-only",
                    "--mute-audio",
                    "--no-crash-upload",
                    "--disable-logging",
                    "--disable-dev-tools",
                    "--window-size=1920,1080"
                ]
            }
            
            # Добавляем прокси если указан
            if account and "proxy" in account:
                proxy_info = self._parse_proxy(account["proxy"])
                if proxy_info:
                    launch_options["proxy"] = proxy_info
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
        
        # Создаем уникальный контекст для аккаунта
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": account.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            "java_script_enabled": True,  # Включаем JavaScript по умолчанию
            "bypass_csp": True  # Обход CSP для лучшей совместимости
        }
        
        # Добавляем прокси если указан
        if account and "proxy" in account:
            proxy_info = self._parse_proxy(account["proxy"])
            if proxy_info:
                context_options["proxy"] = proxy_info
        
        context = await self.browser.new_context(**context_options)
        
        # Применяем методы обхода обнаружения
        enhance_stealth(context)
        
        # Генерируем уникальный ID для контекста
        context_id = account.get("id", "default") if account else "default"
        self.contexts[context_id] = context
        
        return context
    
    async def new_page(self, context: BrowserContext) -> Page:
        """Создание новой страницы с обходом обнаружения"""
        page = await context.new_page()
        
        # Применяем дополнительные методы обхода
        enhance_stealth(page)
        
        return page
    
    def _parse_proxy(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """Разбор строки прокси в формат Playwright"""
        try:
            if proxy_str.startswith("http"):
                # Формат: http://username:password@host:port
                from urllib.parse import urlparse
                parsed = urlparse(proxy_str)
                
                proxy_dict = {
                    "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
                }
                
                if parsed.username and parsed.password:
                    proxy_dict["username"] = parsed.username
                    proxy_dict["password"] = parsed.password
                
                return proxy_dict
            else:
                # Формат: host:port или username:password@host:port
                if "@" in proxy_str:
                    auth, addr = proxy_str.split("@")
                    username, password = auth.split(":")
                    return {
                        "server": f"http://{addr}",
                        "username": username,
                        "password": password
                    }
                else:
                    return {
                        "server": f"http://{proxy_str}"
                    }
        except Exception as e:
            logger.error(f"Error parsing proxy: {e}")
            return None

# Глобальный экземпляр для использования в приложении
browser_manager = BrowserManager()

# Дополнительный класс для работы с nodriver (альтернативный метод)
class NodriverManager:
    def __init__(self):
        self.browser = None
    
    async def startup(self):
        """Инициализация nodriver браузера"""
        # Используем nodriver как альтернативный метод обхода
        self.browser = await uc.start(
            # Аргументы для обхода обнаружения
            headless=False,  # nodriver может работать в headless режиме без обнаружения
            user_data_dir=None,
            browser_args=[
                '--no-first-run',
                '--disable-cloud-import',
                '--disable-save-password-bubble',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Для скорости
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--window-size=1920,1080'
            ]
        )
        
        # Применяем stealth методы
        apply_nodriver_stealth(self.browser)
    
    async def get_tab(self):
        """Получение новой вкладки"""
        if not self.browser:
            await self.startup()
        
        tab = await self.browser.get(url="about:blank")
        return tab
    
    async def shutdown(self):
        """Завершение работы nodriver"""
        if self.browser:
            await self.browser.stop()

# Глобальный экземпляр nodriver менеджера
nodriver_manager = NodriverManager()

# Класс для работы с SeleniumBase
class SeleniumBaseManager:
    def __init__(self):
        self.driver = None
    
    async def startup(self):
        """Инициализация SeleniumBase UC Mode"""
        try:
            from seleniumbase import Driver
            # Используем UC (Undetected-Chromedriver) режим
            self.driver = Driver(
                uc=True,  # Включаем UC режим
                headless=True,
                incognito=False,
                disable_gpu=True,
                locale_code="ru",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        except Exception as e:
            logger.error(f"Error initializing SeleniumBase: {e}")
    
    def get_driver(self):
        """Получение драйвера SeleniumBase"""
        return self.driver
    
    async def shutdown(self):
        """Завершение работы SeleniumBase"""
        if self.driver:
            self.driver.quit()

# Класс для работы с DrissionPage
class DrissionPageManager:
    def __init__(self):
        self.tab = None
        self.session = None
    
    async def startup(self):
        """Инициализация DrissionPage"""
        try:
            from DrissionPage import ChromiumPage, SessionPage
            # Используем ChromiumPage для браузерной автоматизации
            self.tab = ChromiumPage(addr_or_opts="--remote-debugging-port=9222 --no-first-run --disable-blink-features=AutomationControlled --window-size=1920,1080")
        except Exception as e:
            logger.error(f"Error initializing DrissionPage: {e}")
            
        try:
            # Также можем использовать SessionPage для HTTP-запросов
            self.session = SessionPage()
        except Exception as e:
            logger.error(f"Error initializing DrissionPage Session: {e}")
    
    def get_tab(self):
        """Получение вкладки DrissionPage"""
        return self.tab
    
    def get_session(self):
        """Получение сессии DrissionPage"""
        return self.session
    
    async def shutdown(self):
        """Завершение работы DrissionPage"""
        if self.tab:
            self.tab.quit()
        if self.session:
            self.session.close()

# Класс для работы с Patchright (форк Playwright)
class PatchrightManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    async def startup(self):
        """Инициализация Patchright для CDP anti-detection"""
        try:
            import patchright
            from patchright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Запуск браузера с настройками для обхода CDP-детекции
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage", 
                    "--disable-blink-features=AutomationControlled",
                    "--window-size=1920,1080",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-ipc-flooding-protection"
                ]
            )
        except Exception as e:
            logger.error(f"Error initializing Patchright: {e}")
    
    async def new_page(self):
        """Создание новой страницы с помощью Patchright"""
        if not self.browser:
            await self.startup()
        return await self.browser.new_page()
    
    async def shutdown(self):
        """Завершение работы Patchright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Глобальные экземпляры для использования в приложении
seleniumbase_manager = SeleniumBaseManager()
drissionpage_manager = DrissionPageManager()
patchright_manager = PatchrightManager()
