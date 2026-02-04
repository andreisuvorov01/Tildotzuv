"""
Парсер для обработки HTML страниц с закупками из ЕИС (zakupki.gov.ru)
Извлекает объект закупки, начальную цену и даты размещения и окончания подачи заявок
"""

from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from app.services.zakupki_filters import ZakupkiFilters
from typing import List
from bs4 import BeautifulSoup


class ZakupkiParser(BaseParser):
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
        filters = ZakupkiFilters.from_url(base_url) if base_url else ZakupkiFilters()
        
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
                # Очищаем цену от лишних символов
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
