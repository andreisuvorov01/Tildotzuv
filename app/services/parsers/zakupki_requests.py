"""
Request-based парсер для zakupki.gov.ru
Использует requests вместо Playwright для получения данных
"""
import requests
from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from app.services.zakupki_filters import ZakupkiFilters
from typing import List
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ZakupkiRequestsParser(BaseParser):
    domain = "zakupki.gov.ru"

    def should_handle(self, url: str) -> bool:
        return "zakupki.gov.ru" in url

    # Селекторы для поиска элементов закупок
    selectors = {
        "container": "div.search-registry-entry-block.box-shadow-search-input",
        "text": "div.registry-entry__body-value",  # Объект закупки
        "author": "div.registry-entry__body-href a",  # Заказчик
        "rating": "div.price-block__value"  # Начальная цена
    }

    def create_filtered_url(self, base_url: str = None, **filter_params) -> str:
        """Создает URL с фильтрами"""
        filters = ZakupkiFilters()

        # Применяем переданные фильтры
        if 'search_text' in filter_params:
            filters.set_search_text(filter_params['search_text'])
        if 'sort_by' in filter_params:
            filters.set_sort(filter_params['sort_by'], filter_params.get('ascending', True))
        if 'page' in filter_params:
            filters.set_page(filter_params['page'])
        if 'records_per_page' in filter_params:
            filters.set_records_per_page(filter_params['records_per_page'])
        if 'law_types' in filter_params:
            law_types = filter_params['law_types']
            filters.set_law_types(
                law_types.get('fz44', True),
                law_types.get('fz223', True),
                law_types.get('af', True)
            )
        if 'price_range' in filter_params:
            price_range = filter_params['price_range']
            min_val = price_range.get('min')
            max_val = price_range.get('max')
            if min_val and str(min_val).strip():
                min_val = float(min_val)
            else:
                min_val = None
            if max_val and str(max_val).strip():
                max_val = float(max_val)
            else:
                max_val = None
            filters.set_price_range(min_val, max_val)
        if 'date_range' in filter_params:
            date_range = filter_params['date_range']
            filters.set_date_range(date_range.get('from'), date_range.get('to'))

        return filters.build_url()

    def parse(self, html: str, url: str) -> List[ReviewItem]:
        """Парсит HTML с помощью BeautifulSoup"""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Находим все блоки закупок
        containers = soup.select(self.selectors["container"])

        for card in containers:
            # Объект закупки (описание)
            text_element = card.select_one(self.selectors["text"])
            procurement_text = text_element.get_text(strip=True) if text_element else None

            if not procurement_text:
                continue

            # Заказчик
            author_element = card.select_one(self.selectors["author"])
            customer_name = author_element.get_text(strip=True) if author_element else "Неизвестный заказчик"

            # Начальная цена
            price_element = card.select_one(self.selectors["rating"])
            price_text = "Цена не указана"
            if price_element:
                raw_price = price_element.get_text(strip=True)
                # Очищаем цену от HTML-сущностей
                price_text = self._clean_price(raw_price)

            # Номер закупки
            number_element = card.select_one("div.registry-entry__header-mid__number a")
            procurement_number = number_element.get_text(strip=True) if number_element else "Без номера"

            # Формируем текст с дополнительной информацией
            full_text = f"Закупка {procurement_number}: {procurement_text}"

            results.append(ReviewItem(
                text=full_text,
                author=customer_name,
                rating=price_text
            ))

        return results

    def _clean_price(self, price_text: str) -> str:
        """Очищает текст цены от HTML-сущностей и лишних символов"""
        if not price_text:
            return "Цена не указана"

        # Заменяем все проблемные символы
        cleaned = price_text.replace('&#8381;', ' руб.')
        cleaned = cleaned.replace('₽', ' руб.')
        # Удаляем лишние пробелы
        cleaned = ' '.join(cleaned.split())
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
            'Upgrade-Insecure-Requests': '1',
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

