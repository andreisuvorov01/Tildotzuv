import random
import asyncio
import logging
import json
import os
from urllib.parse import urlparse, urlunparse

# Базовые импорты
from app.core.browser import browser_manager
from app.core.humanization import human_scroll, human_mouse_move, login_to_avito
from app.core.network import check_url_accessibility
from app.core.captcha import captcha_solver
from app.core.accounts import account_manager
from app.services.parsers.avito import AvitoParser
from app.services.parsers.zakupki import ZakupkiParser
from app.services.parsers.rts_tender import RtsTenderParser
from app.schemas import ReviewItem

# Опциональные импорты с проверкой
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("cloudscraper not available")

# Создаем заглушки для отсутствующих модулей
class DummyManager:
    def get_tab(self): return None
    def get_session(self): return None
    def get_driver(self): return None
    def new_page(self): return None

# Заглушки для отсутствующих менеджеров
nodriver_manager = DummyManager()
seleniumbase_manager = DummyManager()
drissionpage_manager = DummyManager()
patchright_manager = DummyManager()

# Заглушки для отсутствующих функций
async def get_random_browser_fingerprint(): return {}
async def make_request_with_ja4_fingerprinting(url): return None
async def get_direct_origin_ip(hostname): return None
async def bypass_cloudflare_with_cookies(url, token, ua): return None
async def make_request_with_tls_client(url): return None
def simulate_human_behavior(page): pass

# Заглушка для session_manager
class SessionManager:
    def get_cf_tokens(self): return []
    def get_session(self, sid): return {}
    def update_session(self, sid, data): return True

session_manager = SessionManager()

logger = logging.getLogger(__name__)


class ScraperEngine:
    def __init__(self):
        self.parsers = [AvitoParser(), ZakupkiParser(), RtsTenderParser()]
        self.session_id = None
    
    def set_session_id(self, session_id: str):
        self.session_id = session_id
    
    async def get_session_data(self):
        if self.session_id:
            return session_manager.get_session(self.session_id)
        return None
    
    async def update_session_data(self, data: dict):
        if self.session_id:
            return session_manager.update_session(self.session_id, data)
        return False

    def _get_scraper(self, url: str):
        for parser in self.parsers:
            if parser.should_handle(url):
                return parser
        return self.parsers[0]

    async def run(self, url: str, filters: dict = None, platform: str = None) -> list[ReviewItem]:
        logger.info(f"Starting scraper for URL: {url}")
        scraper = self._get_scraper(url)
        logger.info(f"Selected scraper: {scraper.__class__.__name__}")

        # Применяем фильтры если парсер поддерживает фильтрацию
        if filters and hasattr(scraper, 'create_filtered_url'):
            original_url = url
            url = scraper.create_filtered_url(base_url=url, **filters)
            logger.info(f"Applied filters, original URL: {original_url}")
            logger.info(f"New filtered URL: {url}")

        # Для RTS-тендер пробуем разные методы обхода
        if "rts-tender.ru" in url:
            logger.info("Detected RTS-tender, trying advanced bypass methods...")
            
            # 1. Попробуем cloudscraper
            if CLOUDSCRAPER_AVAILABLE:
                try:
                    results = await self._run_cloudscraper_parser(scraper, url)
                    if results:
                        return results
                except Exception as e:
                    logger.warning(f"Cloudscraper failed: {e}")
            
            # 2. Fallback to Selenium
            try:
                return await self._run_selenium_parser(scraper, url)
            except Exception as e:
                logger.error(f"Selenium also failed: {e}")
                return []

        # Стандартная обработка для других сайтов
        logger.info("Using standard browser-based parser...")

        # 1. Проверяем доступность URL
        logger.info("Checking URL accessibility...")
        if not await check_url_accessibility(url):
            logger.error(f"URL {url} is not accessible")
            raise ValueError(f"URL {url} is not accessible")
        logger.info("URL is accessible")

        # 2. Формируем правильный URL (мобильный для Avito)
        if "avito.ru" in url:
            parsed = urlparse(url)
            if parsed.netloc in ["avito.ru", "www.avito.ru"]:
                parsed = parsed._replace(netloc="m.avito.ru")
                url = urlunparse(parsed)
                logger.info(f"Converted to mobile URL: {url}")

        # 3. Выбираем аккаунт
        account = account_manager.get_random_account()
        if account:
            logger.info(f"Using account: {account.get('id', 'unknown')}")
        else:
            logger.warning("No accounts available! Running anonymously.")

        logger.info("Creating browser context...")
        try:
            context = await browser_manager.get_context(account)
            logger.info("Browser context created successfully")
        except Exception as e:
            logger.error(f"Failed to create browser context: {e}")
            raise

        logger.info("Creating new page...")
        try:
            page = await browser_manager.new_page(context)
            logger.info("Page created successfully")
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            raise

        try:
            page.set_default_timeout(120000)

            # Логин для Avito
            if account and "login" in account and "password" in account and "avito.ru" in url:
                try:
                    profile_check = await page.query_selector(".profile")
                    if not profile_check:
                        logger.info(f"Logging in with account {account['id']}")
                        login_success = await login_to_avito(page, account["login"], account["password"])
                        if not login_success:
                            logger.warning("Login failed, proceeding anonymously")
                        else:
                            logger.info("Login successful")
                    else:
                        logger.info("Already logged in")
                except Exception as e:
                    logger.warning(f"Login check failed: {e}")

            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)

            # CAPTCHA решение
            try:
                captcha_solved = await captcha_solver.detect_and_solve_captcha(page, url)
                if captcha_solved:
                    logger.info("CAPTCHA detected and solved")
                    await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"CAPTCHA solver failed: {e}")

            # Человеческая активность
            try:
                viewport = await page.viewport_size()
                await human_mouse_move(page, 100, 100, viewport['width'] // 2, viewport['height'] // 2)
                await human_scroll(page, 1000)
            except Exception as e:
                logger.warning(f"Humanization failed: {e}")

            await page.screenshot(path="app/debug_result.png")
            html = await page.content()
            logger.info(f"HTML content length: {len(html)} characters")

        except Exception as e:
            logger.error(f"Scraping error: {e}")
            await page.screenshot(path="app/error_final.png")
            raise e
        finally:
            await page.close()
            await context.close()

        return scraper.parse(html, url)

    async def _run_cloudscraper_parser(self, scraper, url: str) -> list[ReviewItem]:
        """Запускает парсер с помощью cloudscraper для обхода Cloudflare"""
        if not CLOUDSCRAPER_AVAILABLE:
            return None
        
        try:
            logger.info("Starting cloudscraper for Cloudflare bypass")
            
            scraper_instance = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=random.uniform(1, 3)
            )

            scraper_instance.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

            response = scraper_instance.get(url, timeout=30)
            logger.info(f"Cloudscraper response status: {response.status_code}")

            if response.status_code == 200:
                html = response.text
                
                # Проверяем на защиту
                protection_indicators = [
                    'Anti-DDoS защита',
                    'cf-browser-verification',
                    'challenge-platform',
                    '__cf_chl_jschl_tk__'
                ]

                if any(indicator in html for indicator in protection_indicators):
                    logger.warning("Cloudflare protection still active")
                    return None

                logger.info("Cloudscraper successfully bypassed protection!")
                return scraper.parse(html, url)
            else:
                logger.warning(f"Cloudscraper failed with status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Cloudscraper error: {e}")
            return None

    async def _run_selenium_parser(self, scraper, url: str) -> list[ReviewItem]:
        """Запускает парсер с помощью Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.support.ui import WebDriverWait
            import time

            logger.info("Starting Selenium parser")

            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info(f"Navigating to {url}")
            driver.get(url)

            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            time.sleep(3)  # Ждем загрузки контента

            html = driver.page_source
            logger.info(f"Retrieved {len(html)} characters")

            results = scraper.parse(html, url)
            driver.quit()
            return results

        except Exception as e:
            logger.error(f"Selenium parsing failed: {e}")
            if 'driver' in locals():
                driver.quit()
            raise
