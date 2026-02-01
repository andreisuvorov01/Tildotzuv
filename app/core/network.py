import asyncio
import logging
import ssl
import socket
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from curl_cffi import aio as cf_aio
from app.core.stealth import create_tls_fingerprinting_headers, get_random_user_agent
import random
import json
import os

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self, proxies_file: str = "proxy_config/config.json"):
        self.proxies = []
        self.current_index = 0
        self.proxies_file = proxies_file
        self.load_proxies()
    
    def add_proxy(self, proxy_url: str):
        """Добавление прокси в список"""
        self.proxies.append(proxy_url)
    
    def get_next_proxy(self) -> Optional[str]:
        """Получение следующего прокси по кругу"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def rotate_proxy(self):
        """Ротация прокси"""
        if self.proxies:
            self.current_index = random.randint(0, len(self.proxies) - 1)
    
    def load_proxies(self, default_proxies: Optional[list] = None):
        """Загрузка прокси из файла"""
        if os.path.exists(self.proxies_file):
            try:
                with open(self.proxies_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.proxies = config.get("proxies", [])
                    logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxies_file}")
            except Exception as e:
                logger.error(f"Failed to load proxies: {e}")
                self.proxies = default_proxies or []
        else:
            logger.warning(f"Proxies file {self.proxies_file} not found")
            self.proxies = default_proxies or []
    
    def get_proxy_stats(self):
        """Получение статистики по прокси"""
        return {
            "total_proxies": len(self.proxies),
            "current_index": self.current_index,
            "next_proxy": self.get_next_proxy()
        }

# Глобальный экземпляр для использования в приложении
proxy_manager = ProxyManager()

async def check_url_accessibility(url: str, timeout: int = 30) -> bool:
    """
    Проверка доступности URL с использованием различных методов
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        # Создание SSL-контекста с настройками для имитации реального браузера
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Попытка подключения через socket
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(hostname, port, ssl=ssl_context),
            timeout=timeout
        )
        
        writer.close()
        await writer.wait_closed()
        return True
        
    except Exception as e:
        logger.warning(f"URL accessibility check failed for {url}: {e}")
        return False

async def make_request_with_ja4_fingerprinting(url: str, headers: Optional[Dict] = None, timeout: int = 30):
    """
    Выполнение запроса с имитацией JA4 TLS fingerprinting
    """
    # Использование curl_cffi для имитации TLS-отпечатков
    try:
        # Создание специфичных для браузера заголовков
        request_headers = create_tls_fingerprinting_headers()
        if headers:
            request_headers.update(headers)
        
        # Использование случайного User-Agent для разнообразия
        request_headers['User-Agent'] = get_random_user_agent()
        
        # Выполнение запроса с помощью curl_cffi
        response = await cf_aio.request(
            url=url,
            headers=request_headers,
            timeout=timeout,
            impersonate=random.choice([
                "chrome_120", "chrome_124", "edge_122", "safari_17_4", "firefox_128"
            ])  # Имитация различных браузеров
        )
        
        return response
    
    except Exception as e:
        logger.error(f"JA4 fingerprinting request failed: {e}")
        return None

# Добавим поддержку tls-client вместо python-tls-client
async def make_request_with_tls_client(url: str, headers: Optional[Dict] = None, timeout: int = 30):
    """
    Выполнение запроса с использованием tls-client для имитации TLS-handshake реальных браузеров
    """
    try:
        import tls_client
        
        # Настройка клиента с имитацией браузера
        session = tls_client.Session(
            client_identifier="chrome_120",  # Имитация Chrome 120
            random_tls_extension_order=True
        )
        
        # Установка заголовков
        request_headers = create_tls_fingerprinting_headers()
        if headers:
            request_headers.update(headers)
        
        # Выполнение запроса
        response = session.get(url, headers=request_headers, timeout=timeout)
        
        return response
        
    except ImportError:
        logger.warning("tls-client not available, falling back to other methods")
        return None
    except Exception as e:
        logger.error(f"TLS client request failed: {e}")
        return None

async def get_direct_origin_ip(domain: str) -> Optional[str]:
    """
    Попытка получить прямой IP-адрес сервера (метод поиска origin IP)
    """
    try:
        # В реальном приложении можно использовать сервисы для поиска origin IP
        # или историю DNS-записей для определения настоящего IP
        import dns.resolver
        
        # Получение A-записей
        answers = dns.resolver.resolve(domain, 'A')
        ips = [str(answer) for answer in answers]
        
        # Возвращаем первый найденный IP
        # В реальном приложении можно реализовать логику проверки каждого IP
        return ips[0] if ips else None
    
    except Exception as e:
        logger.warning(f"Could not resolve origin IP for {domain}: {e}")
        return None

def get_random_browser_fingerprint():
    """
    Генерирует случайный цифровой отпечаток браузера
    """
    fingerprints = {
        'chrome_120': {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'accept_language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'platform': 'Win32',
            'vendor': 'Google Inc.',
            'renderer': 'ANGLE (NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0)',
            'webgl_vendor': 'Google Inc.',
            'webgl_renderer': 'ANGLE (NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0)'
        },
        'firefox_121': {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'accept_language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'platform': 'Win32',
            'vendor': '',
            'renderer': '',
            'webgl_vendor': 'Intel Inc.',
            'webgl_renderer': 'Intel Iris OpenGL Engine'
        },
        'safari_17': {
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'accept_language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'platform': 'MacIntel',
            'vendor': 'Apple Computer, Inc.',
            'renderer': 'webkit',
            'webgl_vendor': 'Apple Inc.',
            'webgl_renderer': 'Apple M1 Pro'
        }
    }
    
    return random.choice(list(fingerprints.values()))

async def bypass_cloudflare_with_cookies(url: str, cf_clearance_token: str, user_agent: str):
    """
    Использование cf_clearance токена для обхода Cloudflare
    """
    try:
        headers = {
            'User-Agent': user_agent,
            'Cookie': f'cf_clearance={cf_clearance_token}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = await cf_aio.request(
            url=url,
            headers=headers,
            timeout=30,
            impersonate="chrome_120"
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Cookie-based Cloudflare bypass failed: {e}")
        return None