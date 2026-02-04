"""
Парсер для РТС-тендер (rts-tender.ru) с обходом Cloudflare
"""
import requests
from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from typing import List
from bs4 import BeautifulSoup
import logging
import time
import random
import re

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

class RtsTenderParser(BaseParser):
    domain = "rts-tender.ru"
    
    def should_handle(self, url: str) -> bool:
        return "rts-tender.ru" in url
    
    # Селекторы для поиска элементов тендеров
    selectors = {
        "container": [
            ".tender-item", ".search-result-item", ".lot-item", ".tender-row", "tr",
            ".cards", ".card-item", ".tender-card", ".search-result", ".result-item",
            "[class*='tender']", "[class*='lot']", "[class*='procurement']"
        ],
        "text": [
            ".tender-name", ".lot-name", ".tender-subject", ".title", "h3", "h4", "a",
            "[data-annotation='PurchaseName']", ".card-item__title", ".tender-title",
            "[class*='name']", "[class*='subject']", "[class*='title']"
        ],
        "author": [
            ".customer-name", ".organizer", ".company-name", ".customer", ".card-item__organization-main",
            ".card-item__organization-title", ".organizer-name", ".customer-info",
            "[class*='customer']", "[class*='company']", "[class*='org']"
        ],
        "rating": [
            ".price", ".start-price", ".initial-price", ".cost", ".amount", ".card-item__properties-desc",
            ".tender-price", ".card-item__properties-name", "[class*='price']", "[class*='cost']",
            "[class*='sum']", "[class*='amount']"
        ]
    }
    
    def create_filtered_url(self, base_url: str = None, **filter_params) -> str:
        """Создает URL с фильтрами для РТС-тендер"""
        base = base_url or "https://www.rts-tender.ru/poisk/poisk-44-fz"
        params = []
        
        if 'search_text' in filter_params and filter_params['search_text']:
            params.append(f"keywords={filter_params['search_text']}")
        
        if 'records_per_page' in filter_params:
            params.append(f"limit={filter_params['records_per_page']}")
            
        if 'page' in filter_params and filter_params['page'] > 1:
            params.append(f"page={filter_params['page']}")
        
        if params:
            return f"{base}?{'&'.join(params)}"
        return base
    
    def parse(self, html: str, url: str) -> List[ReviewItem]:
        """Парсит HTML с помощью BeautifulSoup"""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        # Проверяем на Cloudflare защиту
        cloudflare_indicators = [
            'Anti-DDoS защита',
            'cf-browser-verification',
            'challenge-platform',
            '__cf_chl_jschl_tk__',
            'DDoS protection by Cloudflare',
            'Checking your browser',
            'Access denied',
            'blocked',
            'cloudflare',
            'Attention Required! | Cloudflare'
        ]
        
        if any(indicator.lower() in html.lower() for indicator in cloudflare_indicators):
            logger.warning("Cloudflare protection detected in HTML")
            return [ReviewItem(
                text="РТС-тендер: Обнаружена защита Cloudflare. Требуется браузерный обход.",
                author="Система защиты",
                rating="Заблокировано"
            )]
        
        logger.info("No Cloudflare protection detected - proceeding with parsing")
        
        # Проверяем наличие признаков закупок на странице
        procurement_keywords = ['тендер', 'закупк', 'лот', 'аукцион', 'конкурс', 'процедур', 'обеспечение', 'поставка', 'работ', 'услуг', '44-фз', '223-фз']
        html_lower = html.lower()
        has_procurement_indicators = any(keyword in html_lower for keyword in procurement_keywords)
        
        if not has_procurement_indicators:
            logger.warning("No procurement indicators found in HTML")
            return [ReviewItem(
                text="На странице не обнаружены признаки наличия тендеров. Возможно, защита Cloudflare не полностью снята или структура сайта изменилась.",
                author="Техническая информация",
                rating="Нет данных"
            )]
        
        # Попробуем разные подходы к нахождению контейнеров
        containers = []
        
        # Сначала пробуем основные селекторы
        for selector_group in [self.selectors["container"], ["tr", ".row", ".item", ".card", ".result"]]:
            for selector in selector_group:
                elements = soup.select(selector)
                if elements and len(elements) > 0:
                    containers = elements
                    logger.info(f"Found {len(elements)} containers using selector: {selector}")
                    break
            if containers:
                break
        
        # Если не нашли, пробуем универсальные селекторы
        if not containers:
            universal_selectors = [
                "[class*='tender']", "[class*='lot']", "[class*='procurement']",
                "[class*='search']", "[class*='auction']", "[class*='card']",
                "tr", ".row", ".item", ".result", ".entry", ".post"
            ]
            for selector in universal_selectors:
                elements = soup.select(selector)
                if len(elements) > 0:
                    # Фильтруем элементы, которые содержат ключевые слова
                    filtered_elements = []
                    for el in elements:
                        el_text = el.get_text().lower()
                        if any(keyword in el_text for keyword in ['тендер', 'закупк', 'лот', 'аукцион', 'конкурс', 'обеспечение', 'поставка', 'работ', 'услуг']):
                            filtered_elements.append(el)
                    
                    if len(filtered_elements) > 0:
                        containers = filtered_elements
                        logger.info(f"Found {len(filtered_elements)} potential containers with keyword filtering using selector: {selector}")
                        break
        
        # Если все еще не нашли, ищем по содержимому
        if not containers:
            # Ищем div или другие элементы, которые содержат ключевые слова
            all_elements = soup.find_all(['div', 'article', 'section', 'tr', 'td', 'li', 'article', 'span', 'p'])
            for element in all_elements:
                element_text = element.get_text().lower()
                keyword_matches = sum(1 for keyword in ['тендер', 'закупк', 'лот', 'аукцион', 'конкурс', 'обеспечение', 'поставка', 'работ', 'услуг'] if keyword in element_text)
                if keyword_matches >= 2:  # Если есть хотя бы 2 ключевых слова
                    containers.append(element)
        
        logger.info(f"Processing {len(containers)} potential tender containers")
        
        processed_count = 0
        for card in containers[:15]:  # Ограничим до 15 результатов
            if processed_count >= 15:
                break
                
            # Извлекаем название тендера
            tender_text = None
            for selector in self.selectors["text"]:
                text_element = card.select_one(selector)
                if text_element:
                    tender_text = text_element.get_text(strip=True)
                    if tender_text and len(tender_text) >= 15:
                        break
            
            # Если не нашли в стандартных местах, ищем по ключевым словам в любом месте элемента
            if not tender_text or len(tender_text) < 15:
                card_text = card.get_text()
                sentences = card_text.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in ['тендер', 'закупк', 'лот', 'аукцион', 'конкурс']):
                        tender_text = sentence.strip()
                        if len(tender_text) >= 15:
                            break
            
            if not tender_text or len(tender_text) < 15:
                continue  # Пропускаем, если не нашли подходящий текст
                
            # Извлекаем заказчика
            customer_name = "Заказчик не указан"
            for selector in self.selectors["author"]:
                author_element = card.select_one(selector)
                if author_element:
                    customer_name = author_element.get_text(strip=True)
                    if customer_name and customer_name != "Заказчик не указан":
                        break
            
            # Извлекаем цену
            price_text = "Цена не указана"
            for selector in self.selectors["rating"]:
                price_element = card.select_one(selector)
                if price_element:
                    raw_price = price_element.get_text(strip=True)
                    price_text = self._clean_price(raw_price)
                    if price_text != "Цена не указана":
                        break
            
            # Ищем номер тендера
            tender_number = ""
            number_selectors = ["a[href*='lot']", ".number", ".tender-number", "td:first-child", "[data-id]", "[href*='id']", ".card-item__about a"]
            for selector in number_selectors:
                number_element = card.select_one(selector)
                if number_element:
                    tender_number = number_element.get_text(strip=True)
                    if tender_number:
                        break
        
            # Формируем текст
            if tender_number and tender_text and not tender_text.startswith(f"Тендер №{tender_number}"):
                full_text = f"Тендер №{tender_number}: {tender_text}"
            else:
                full_text = f"Тендер: {tender_text}"
            
            results.append(ReviewItem(
                text=full_text,
                author=customer_name,
                rating=price_text
            ))
            
            processed_count += 1
        
        # Если ничего не нашли, возвращаем информационное сообщение
        if not results:
            return [ReviewItem(
                text="На странице РТС-тендер не найдено тендеров. Возможно, изменилась структура сайта, требуется авторизация или защита Cloudflare не полностью снята.",
                author="Техническая информация",
                rating="Нет данных"
            )]
            
        return results
    
    def _clean_price(self, price_text: str) -> str:
        """Очищает текст цены"""
        if not price_text:
            return "Цена не указана"
            
        # Удаляем лишние символы
        cleaned = price_text.replace('\n', ' ').replace('\r', ' ')
        cleaned = ' '.join(cleaned.split())
        
        # Ищем паттерны цен
        price_match = re.search(r'[\d\s,.]+[\s]*(руб|рублей|р\.|₽|\$|€|USD|EUR)', cleaned, re.IGNORECASE)
        if price_match:
            return price_match.group(0).strip()
        
        return cleaned.strip()
    
    def fetch_html(self, url: str) -> str:
        """
        Получает HTML страницы с помощью cloudscraper для обхода Cloudflare
        """
        if not CLOUDSCRAPER_AVAILABLE:
            logger.warning("cloudscraper not available, using fallback requests")
            return self._fallback_fetch(url)

        try:
            # Попробуем использовать cloudscraper для обхода Cloudflare
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=3
            )
            
            # Установим заголовки для имитации реального браузера
            scraper.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logger.info(f"Attempting to fetch URL with cloudscraper: {url}")
            
            response = scraper.get(url, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Successfully fetched {len(response.text)} characters")
                return response.text
            else:
                logger.warning(f"Received status code {response.status_code}, response length: {len(response.text)}")
                return response.text
                
        except Exception as e:
            logger.error(f"Cloudscraper failed: {e}")
            # В случае неудачи с cloudscraper, используем обычный requests
            return self._fallback_fetch(url)
    
    def _fallback_fetch(self, url: str) -> str:
        """
        Запасной метод получения HTML с использованием обычного requests
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15.7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.rts-tender.ru/'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            logger.info(f"Fetching URL with fallback method: {url}")
            
            # Делаем первый запрос
            response = session.get(url, timeout=30, allow_redirects=True)
            
            logger.info(f"Fallback response status: {response.status_code}")
            
            # Если получили Cloudflare challenge, пробуем подождать и повторить
            if response.status_code == 503 or 'cloudflare' in response.text.lower():
                logger.info("Cloudflare challenge detected, waiting before retry...")
                time.sleep(random.uniform(5, 10))  # Ждем случайное время
                
                # Обновляем User-Agent и пробуем снова
                headers['User-Agent'] = random.choice(user_agents)
                session.headers.update(headers)
                
                response = session.get(url, timeout=30, allow_redirects=True)
                logger.info(f"Retry response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Successfully fetched {len(response.text)} characters with fallback method")
                return response.text
            else:
                logger.warning(f"Fallback method returned status {response.status_code}")
                return f"<html><body>HTTP {response.status_code}: Сайт РТС-тендер недоступен</body></html>"
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {url}")
            return "<html><body>Timeout: Сайт РТС-тендер не отвечает</body></html>"
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return f"<html><body>Ошибка подключения к РТС-тендер: {str(e)}</body></html>"
