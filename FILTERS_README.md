# Фильтры для zakupki.gov.ru

Добавлена полная поддержка фильтров для парсинга сайта zakupki.gov.ru через URL параметры.

## Доступные фильтры

### 1. Поисковый запрос
```python
filters = {"search_text": "медицинское оборудование"}
```

### 2. Сортировка
```python
filters = {
    "sort_by": "PRICE",  # UPDATE_DATE, PUBLISH_DATE, PRICE, RELEVANCE
    "ascending": False   # True для возрастания, False для убывания
}
```

### 3. Пагинация
```python
filters = {
    "page": 2,              # Номер страницы
    "records_per_page": 50  # 10, 20, 50, 100
}
```

### 4. Типы законов
```python
filters = {
    "law_types": {
        "fz44": True,   # 44-ФЗ
        "fz223": True,  # 223-ФЗ  
        "af": False     # Антимонопольное законодательство
    }
}
```

### 5. Диапазон цен
```python
filters = {
    "price_range": {
        "min": 100000,    # Минимальная цена
        "max": 1000000    # Максимальная цена
    }
}
```

### 6. Диапазон дат
```python
filters = {
    "date_range": {
        "from": "01.01.2026",  # Дата от (DD.MM.YYYY)
        "to": "31.12.2026"     # Дата до (DD.MM.YYYY)
    }
}
```

## Использование через API

### Базовый запрос
```bash
curl -X POST "http://localhost:8000/api/v1/extract-reviews" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
     }'
```

### Запрос с фильтрами
```bash
curl -X POST "http://localhost:8000/api/v1/extract-reviews" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://zakupki.gov.ru/epz/order/extendedsearch/results.html",
       "filters": {
         "search_text": "компьютеры",
         "sort_by": "PRICE",
         "ascending": false,
         "records_per_page": 20,
         "law_types": {
           "fz44": true,
           "fz223": false,
           "af": false
         },
         "price_range": {
           "min": 50000,
           "max": 500000
         }
       }
     }'
```

## Использование в коде

### Создание URL с фильтрами
```python
from app.services.parsers.zakupki import ZakupkiParser

parser = ZakupkiParser()

# Простой фильтр
url = parser.create_filtered_url(search_text="мебель")

# Сложный фильтр
url = parser.create_filtered_url(
    search_text="строительство",
    sort_by="PRICE",
    ascending=False,
    page=2,
    records_per_page=50,
    law_types={"fz44": True, "fz223": True, "af": False},
    price_range={"min": 1000000, "max": 10000000}
)
```

### Работа с классом фильтров
```python
from app.services.zakupki_filters import ZakupkiFilters

# Создание фильтров
filters = ZakupkiFilters()
filters.set_search_text("медицина") \
       .set_sort("PRICE", ascending=False) \
       .set_page(3) \
       .set_records_per_page(20) \
       .set_law_types(fz44=True, fz223=False, af=False)

url = filters.build_url()

# Парсинг существующего URL
filters = ZakupkiFilters.from_url(existing_url)
params = filters.get_filters_dict()
```

## Примеры сгенерированных URL

### 1. Поиск медицинского оборудования
```
https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&currencyIdGeneral=-1&searchString=медицинское+оборудование
```

### 2. Только 44-ФЗ, сортировка по цене (убывание)
```
https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&sortBy=PRICE&fz44=on&currencyIdGeneral=-1
```

### 3. Фильтр по цене от 100,000 до 1,000,000
```
https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&currencyIdGeneral=-1&priceFrom=100000&priceTo=1000000
```

## Структура ответа API

```json
{
  "source_url": "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?...",
  "reviews_count": 10,
  "reviews": [
    {
      "text": "Закупка № 32615629153: Право заключения договора...",
      "author": "АКЦИОНЕРНОЕ ОБЩЕСТВО \"УСТЬ-СРЕДНЕКАНЭССТРОЙ\"",
      "rating": "4 484 426,56 руб."
    }
  ],
  "applied_filters": {
    "search_text": "медицинское оборудование",
    "sort_by": "PRICE",
    "ascending": false
  }
}
```

## Тестирование

### 1. Тест фильтров
```bash
python test_filters.py
```

### 2. Тест API с фильтрами
```bash
python test_api_filters.py
```

## Поддерживаемые параметры URL

| Параметр | Описание | Возможные значения |
|----------|----------|-------------------|
| `searchString` | Поисковый запрос | Любой текст |
| `sortBy` | Сортировка | UPDATE_DATE, PUBLISH_DATE, PRICE, RELEVANCE |
| `sortDirection` | Направление сортировки | true (возрастание), false (убывание) |
| `pageNumber` | Номер страницы | 1, 2, 3, ... |
| `recordsPerPage` | Записей на странице | _10, _20, _50, _100 |
| `fz44` | 44-ФЗ | on (включено) |
| `fz223` | 223-ФЗ | on (включено) |
| `af` | Антимонопольное законодательство | on (включено) |
| `priceFrom` | Цена от | Число |
| `priceTo` | Цена до | Число |
| `publishDateFrom` | Дата размещения от | DD.MM.YYYY |
| `publishDateTo` | Дата размещения до | DD.MM.YYYY |

## Особенности

1. **URL-based подход** - все фильтры передаются через URL параметры
2. **Обратная совместимость** - работает с существующими URL
3. **Валидация** - автоматическая проверка корректности параметров
4. **Цепочка вызовов** - удобный fluent interface для настройки фильтров