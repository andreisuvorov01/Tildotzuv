"""
Парсер для Национальной Электронной Площадки (НЭП) (neptek.ru)
"""
import requests
from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from typing import List
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class NepParser(BaseParser):
    domain = "neptek.ru"

    def should_handle(self, url: str) -> bool:
        return "neptek.ru" in url or "nep.ru" in url

    # Селекторы для поиска элементов закупок на НЭП
    selectors = {
        "container": ".trade-item, .tender-card, .procedure-item",
        "text": ".trade-name, .tender-title, h3, h4",
        "author": ".customer-name, .organizer, .company-name",
        "rating": ".trade-price, .price, .cost"
    }

    def create_filtered_url(self, base_url: str = None, **filter_params) -> str:
        """Создает URL с фильтрами для НЭП"""
        base = base_url or "https://neptek.ru/trades"
        params = []

        if 'search_text' in filter_params and filter_params['search_text']:
            params.append(f"search={filter_params['search_text']}")

        if 'records_per_page' in filter_params:
            params.append(f"limit={filter_params['records_per_page']}")

        if params:
            return f"{base}?{'&'.join(params)}"
        return base

    def parse(self, html: str, url: str) -> List[ReviewItem]:
        """Парсит HTML с помощью BeautifulSoup"""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Находим все блоки закупок
        containers = soup.select(self.selectors["container"])

        if not containers:
            # Попробуем другие селекторы
            containers = soup.select(".trade, .tender, .procedure")

        for card in containers[:10]:  # Ограничим до 10 результатов
            # Название закупки
            text_element = card.select_one(self.selectors["text"])
            if not text_element:
                text_element = card.select_one("h3, h4, .title, a")

            procurement_text = text_element.get_text(strip=True) if text_element else "Название не указано"

            # Заказчик
            author_element = card.select_one(self.selectors["author"])
            if not author_element:
                author_element = card.select_one(".customer, .organizer, .company")

            customer_name = author_element.get_text(strip=True) if author_element else "Заказчик не указан"

            # Цена
            price_element = card.select_one(self.selectors["rating"])
            if not price_element:
                price_element = card.select_one(".price, .cost, .amount, .sum")

            price_text = "Цена не указана"
            if price_element:
                raw_price = price_element.get_text(strip=True)
                price_text = self._clean_price(raw_price)

            # Номер (если есть)
            number_element = card.select_one(".trade-number, .tender-number, .procedure-number")
            procedure_number = number_element.get_text(strip=True) if number_element else ""

            # Формируем текст
            full_text = f"{procedure_number} {procurement_text}".strip() if procedure_number else procurement_text

            results.append(ReviewItem(
                text=full_text,
                author=customer_name,
                rating=price_text
            ))

        return results

    def _clean_price(self, price_text: str) -> str:
        """Очищает текст цены"""
        if not price_text:
            return "Цена не указана"

        # Удаляем лишние пробелы и символы
        cleaned = price_text.replace('\n', ' ').replace('\r', ' ')
        cleaned = ' '.join(cleaned.split())

        # Ищем паттерны цен
        import re
        price_match = re.search(r'[\d\s,]+\s*(руб|рублей|р\.|₽|\$|€)', cleaned, re.IGNORECASE)
        if price_match:
            return price_match.group(0).strip()

        return cleaned.strip()

    def fetch_html(self, url: str) -> str:
        """
        Получает HTML страницы с помощью requests
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://neptek.ru/'
        }

        try:
            logger.info(f"Fetching URL with requests: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            logger.info(f"Successfully fetched {len(response.text)} characters")
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise

