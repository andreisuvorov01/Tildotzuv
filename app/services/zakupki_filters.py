from typing import Dict, Optional
from urllib.parse import urlencode, urlparse, parse_qs


class ZakupkiFilters:
    """Класс для работы с фильтрами zakupki.gov.ru"""
    
    BASE_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
    
    # Доступные фильтры
    SORT_OPTIONS = {
        "UPDATE_DATE": "Дате обновления",
        "PUBLISH_DATE": "Дате размещения", 
        "PRICE": "Цене",
        "RELEVANCE": "Релевантности"
    }
    
    RECORDS_PER_PAGE = {
        "_10": 10,
        "_20": 20,
        "_50": 50,
        "_100": 100
    }
    
    def __init__(self):
        self.filters = {
            "morphology": "on",
            "pageNumber": "1",
            "sortDirection": "false",
            "recordsPerPage": "_10",
            "sortBy": "UPDATE_DATE",
            "fz44": "on",
            "fz223": "on", 
            "af": "on",
            "currencyIdGeneral": "-1"
        }
    
    def set_search_text(self, text: str) -> 'ZakupkiFilters':
        """Установить поисковый запрос"""
        if text:
            self.filters["searchString"] = text
        return self
    
    def set_sort(self, sort_by: str, ascending: bool = True) -> 'ZakupkiFilters':
        """Установить сортировку"""
        if sort_by in self.SORT_OPTIONS:
            self.filters["sortBy"] = sort_by
            self.filters["sortDirection"] = "true" if ascending else "false"
        return self
    
    def set_page(self, page: int) -> 'ZakupkiFilters':
        """Установить номер страницы"""
        self.filters["pageNumber"] = str(max(1, page))
        return self
    
    def set_records_per_page(self, count: int) -> 'ZakupkiFilters':
        """Установить количество записей на странице"""
        for key, value in self.RECORDS_PER_PAGE.items():
            if value == count:
                self.filters["recordsPerPage"] = key
                break
        return self
    
    def set_law_types(self, fz44: bool = True, fz223: bool = True, af: bool = True) -> 'ZakupkiFilters':
        """Установить типы законов о закупках"""
        if fz44:
            self.filters["fz44"] = "on"
        else:
            self.filters.pop("fz44", None)
            
        if fz223:
            self.filters["fz223"] = "on"
        else:
            self.filters.pop("fz223", None)
            
        if af:
            self.filters["af"] = "on"
        else:
            self.filters.pop("af", None)
        return self
    
    def set_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> 'ZakupkiFilters':
        """Установить диапазон цен"""
        if min_price is not None and str(min_price).strip():
            self.filters["priceFrom"] = str(int(float(min_price)))
        if max_price is not None and str(max_price).strip():
            self.filters["priceTo"] = str(int(float(max_price)))
        return self
    
    def set_date_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> 'ZakupkiFilters':
        """Установить диапазон дат (формат: DD.MM.YYYY)"""
        if date_from:
            self.filters["publishDateFrom"] = date_from
        if date_to:
            self.filters["publishDateTo"] = date_to
        return self
    
    def build_url(self) -> str:
        """Построить URL с фильтрами"""
        return f"{self.BASE_URL}?{urlencode(self.filters)}"
    
    @classmethod
    def from_url(cls, url: str) -> 'ZakupkiFilters':
        """Создать объект фильтров из URL"""
        instance = cls()
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Преобразуем параметры из списков в строки
        for key, values in params.items():
            if values:
                instance.filters[key] = values[0]
        
        return instance
    
    def get_filters_dict(self) -> Dict[str, str]:
        """Получить словарь фильтров"""
        return self.filters.copy()