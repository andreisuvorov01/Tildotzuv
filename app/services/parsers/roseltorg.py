"""
Парсер для Росэлторг (roseltorg.ru)
"""
import requests
from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from typing import List
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class RoseltorgParser(BaseParser):
    domain = "roseltorg.ru"

    def should_handle(self, url: str) -> bool:
        return "roseltorg.ru" in url

    # Селекторы для поиска элементов закупок на Росэлторг
    selectors = {
        "container": ".search-results__item",
        "text": ".search-results__item",  # Сам элемент содержит текст
        "author": ".search-results__item",  # Заказчик тоже в тексте элемента
        "rating": ".search-results__item"   # Цена тоже в тексте элемента
    }

    def create_filtered_url(self, base_url: str = None, **filter_params) -> str:
        """Создает URL с фильтрами для Росэлторг"""
        base = "https://www.roseltorg.ru/procedures/search"
        params = [
            "sale=1",  # Продажа
            "status%5B%5D=5",  # Активные
            "status%5B%5D=0",  # Черновики
            "status%5B%5D=1",  # Подготовка
            "currency=all",    # Все валюты
            "place=fkr",       # ФКР
            "source%5B%5D=13"  # Источник
        ]

        # Добавляем фильтры пользователя
        if 'search_text' in filter_params and filter_params['search_text']:
            params.append(f"search={filter_params['search_text']}")

        if 'page' in filter_params and filter_params['page'] > 1:
            params.append(f"page={filter_params['page']}")

        return f"{base}?{'&'.join(params)}"

    def parse(self, html: str, url: str) -> List[ReviewItem]:
        """Парсит HTML с помощью BeautifulSoup"""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Находим все блоки закупок
        containers = soup.select(self.selectors["container"])

        for card in containers[:10]:  # Ограничим до 10 результатов
            # Получаем полный текст элемента
            full_text = card.get_text(strip=True)

            if len(full_text) < 20:  # Пропускаем слишком короткие элементы
                continue

            # Разбираем текст на компоненты
            procurement_text = full_text

            # Ищем паттерны цен в тексте
            price_text = self._extract_price_from_text(full_text)

            # Ищем информацию о заказчике
            customer_name = self._extract_customer_from_text(full_text)

            # Ищем номер процедуры
            procedure_number = self._extract_number_from_text(full_text)

            # Формируем финальный текст
            if procedure_number:
                display_text = f"Процедура №{procedure_number}: {procurement_text[:200]}..."
            else:
                display_text = procurement_text[:250] + "..." if len(procurement_text) > 250 else procurement_text

            results.append(ReviewItem(
                text=display_text,
                author=customer_name,
                rating=price_text
            ))

        return results

    def _extract_price_from_text(self, text: str) -> str:
        """Извлекает цену из текста"""
        import re

        # Ищем различные паттерны цен
        price_patterns = [
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{2})?\s*(?:руб|рублей|р\.|₽))',
            r'(\d+(?:,\d{2})?\s*(?:руб|рублей|р\.|₽))',
            r'(\d+(?:\.\d{2})?\s*(?:руб|рублей|р\.|₽))'
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Цена не указана"

    def _extract_customer_from_text(self, text: str) -> str:
        """Извлекает информацию о заказчике из текста"""
        import re

        # Ищем паттерны с заказчиком
        customer_patterns = [
            r'(?:Заказчик|Организатор|Компания):\s*([^,\n]{10,50})',
            r'(?:Заказчик|Организатор):\s*([^,\n]{10,50})',
            r'([А-ЯЁ][а-яё\s]{10,50}(?:ООО|АО|ПАО|ЗАО|ГУП|МУП))'
        ]

        for pattern in customer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Заказчик не указан"

    def _extract_number_from_text(self, text: str) -> str:
        """Извлекает номер процедуры из текста"""
        import re

        # Ищем паттерны номеров
        number_patterns = [
            r'(?:№|N)\s*(\d{6,})',
            r'(\d{6,})',
            r'(\d{2}-\d{2}-\d{6})'
        ]

        for pattern in number_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return ""

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
            'Referer': 'https://roseltorg.ru/'
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
