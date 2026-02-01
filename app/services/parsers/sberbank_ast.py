"""
Парсер для Сбербанк-АСТ (sberbank-ast.ru)
"""
import requests
from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from typing import List
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class SberbankAstParser(BaseParser):
    domain = "sberbank-ast.ru"

    def should_handle(self, url: str) -> bool:
        return "sberbank-ast.ru" in url

    # Селекторы для поиска элементов закупок на Сбербанк-АСТ
    selectors = {
        "container": ".purchase-item, .tender-card, .procedure-item",
        "text": ".purchase-name, .tender-title, h3, h4",
        "author": ".customer-name, .organizer, .company-name",
        "rating": ".purchase-price, .price, .cost"
    }

    def create_filtered_url(self, base_url: str = None, **filter_params) -> str:
        """Создает URL с фильтрами для Сбербанк-АСТ"""
        base = base_url or "https://www.sberbank-ast.ru/purchaseList.aspx"
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

        # Проверяем, есть ли JavaScript challenge (если да, то браузер не справился)
        if 'Challenge=' in html:
            logger.warning("Sberbank-AST.ru JavaScript challenge still present - browser may need different approach")
            return [ReviewItem(
                text="Сбербанк-АСТ: JavaScript challenge не удалось обойти. Попробуйте другой браузер или подождите.",
                author="Техническая информация",
                rating="Недоступно"
            )]

        logger.info("No JavaScript challenge detected - proceeding with parsing")

        # Находим все блоки закупок
        containers = soup.select(self.selectors["container"])

        if not containers:
            # Попробуем другие селекторы для Сбербанк-АСТ
            containers = soup.select(".purchase, .tender, .procedure, tr, .row, .item")

        logger.info(f"Found {len(containers)} potential procurement containers")

        if not containers:
            # Если ничего не нашли, попробуем найти таблицы или другие структуры
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables on page")

            if tables:
                # Ищем строки в таблицах
                for table in tables:
                    rows = table.find_all('tr')
                    logger.info(f"Table has {len(rows)} rows")
                    for row in rows[1:11]:  # Пропускаем заголовок, берем первые 10 строк
                        cells = row.find_all('td')
                        if len(cells) >= 3:  # Минимум 3 колонки
                            procurement_text = cells[1].get_text(strip=True) if len(cells) > 1 else "Название не указано"
                            customer_name = cells[2].get_text(strip=True) if len(cells) > 2 else "Заказчик не указан"
                            price_text = self._extract_price_from_row(cells)

                            if procurement_text and len(procurement_text) > 10:  # Фильтруем пустые или слишком короткие
                                results.append(ReviewItem(
                                    text=procurement_text,
                                    author=customer_name,
                                    rating=price_text
                                ))

        # Если нашли контейнеры через селекторы
        for card in containers[:10]:  # Ограничим до 10 результатов
            # Название закупки
            text_element = card.select_one(self.selectors["text"])
            if not text_element:
                text_element = card.select_one("h3, h4, .title, a, td:nth-child(2)")

            procurement_text = text_element.get_text(strip=True) if text_element else "Название не указано"

            # Заказчик
            author_element = card.select_one(self.selectors["author"])
            if not author_element:
                author_element = card.select_one(".customer, .organizer, .company, td:nth-child(3)")

            customer_name = author_element.get_text(strip=True) if author_element else "Заказчик не указан"

            # Цена
            price_element = card.select_one(self.selectors["rating"])
            if not price_element:
                price_element = card.select_one(".price, .cost, .amount, .sum, td:nth-child(4)")

            price_text = "Цена не указана"
            if price_element:
                raw_price = price_element.get_text(strip=True)
                price_text = self._clean_price(raw_price)

            # Номер (если есть)
            number_element = card.select_one(".purchase-number, .tender-number, .procedure-number, td:nth-child(1)")
            procedure_number = number_element.get_text(strip=True) if number_element else ""

            # Формируем текст
            if procedure_number and procedure_number != procurement_text:
                full_text = f"{procedure_number}: {procurement_text}"
            else:
                full_text = procurement_text

            # Добавляем только если текст достаточно информативный
            if len(full_text) > 15 and full_text != "Название не указано":
                results.append(ReviewItem(
                    text=full_text,
                    author=customer_name,
                    rating=price_text
                ))

        if not results:
            return [ReviewItem(
                text="На странице Сбербанк-АСТ не найдено процедур. Возможно, требуется другой подход к парсингу.",
                author="Техническая информация",
                rating="Нет данных"
            )]

        return results

    def _extract_price_from_row(self, cells):
        """Извлекает цену из строки таблицы"""
        for cell in cells:
            text = cell.get_text(strip=True)
            if any(keyword in text.lower() for keyword in ['руб', 'рублей', 'р.', '₽', 'тыс', 'млн', 'млрд']):
                return self._clean_price(text)
        return "Цена не указана"

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
            'Referer': 'https://www.sberbank-ast.ru/'
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

