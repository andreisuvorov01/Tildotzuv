# Парсер zakupki.gov.ru

Добавлена поддержка парсинга сайта государственных закупок zakupki.gov.ru в существующий проект парсера отзывов.

## Что добавлено

### 1. Новый парсер ZakupkiParser
- Файл: `app/services/parsers/zakupki.py`
- Наследуется от `BaseParser`
- Парсит страницы результатов поиска закупок
- Извлекает: номер закупки, описание, заказчика, начальную цену

### 2. Интеграция в существующую архитектуру
- Парсер добавлен в `ScraperEngine`
- Использует существующую схему `ReviewItem`
- Совместим с API эндпоинтом `/api/v1/extract-reviews`

### 3. Тестовые скрипты
- `test_zakupki.py` - тест парсера на локальном HTML файле
- `test_api_zakupki.py` - тест через API

## Поддерживаемые URL

Парсер работает с URL вида:
```
https://zakupki.gov.ru/epz/order/extendedsearch/results.html?...
```

Пример URL для тестирования:
```
https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=Дате+размещения&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&currencyIdGeneral=-1
```

## Структура данных

Парсер возвращает данные в формате `ReviewItem`:
- `text` - Номер и описание закупки
- `author` - Наименование заказчика
- `rating` - Начальная цена закупки

Пример:
```json
{
  "text": "Закупка № 32615629153: Право заключения договора на ОКПД2 28.22.13 Поставка домкратов...",
  "author": "АКЦИОНЕРНОЕ ОБЩЕСТВО \"УСТЬ-СРЕДНЕКАНЭССТРОЙ\"",
  "rating": "4 484 426,56 руб."
}
```

## Тестирование

### 1. Тест парсера на локальном файле
```bash
python test_zakupki.py
```

### 2. Тест через API
Сначала запустите сервер:
```bash
python app/main.py
```

Затем в другом терминале:
```bash
python test_api_zakupki.py
```

### 3. Тест через curl
```bash
curl -X POST "http://localhost:8000/api/v1/extract-reviews" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=Дате+размещения&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&currencyIdGeneral=-1"}'
```

## Особенности реализации

1. **Минимальные изменения**: Парсер интегрирован в существующую архитектуру без нарушения работы других компонентов

2. **Совместимость**: Использует ту же схему данных `ReviewItem`, что и парсер Avito

3. **Обработка кодировки**: Корректно обрабатывает русские символы и HTML-сущности

4. **Селекторы CSS**: Использует стабильные CSS-селекторы для извлечения данных

## Селекторы

Парсер использует следующие CSS-селекторы:
- `container`: `div.search-registry-entry-block.box-shadow-search-input` - блоки закупок
- `text`: `div.registry-entry__body-value` - описание закупки
- `author`: `div.registry-entry__body-href a` - заказчик
- `rating`: `div.price-block__value` - начальная цена

## Ограничения

1. Парсер работает только со страницами результатов поиска
2. Не поддерживает детальные страницы отдельных закупок
3. Извлекает только основную информацию (без дат, статусов и т.д.)

## Расширение функциональности

Для добавления новых полей:
1. Расширьте схему `ReviewItem` в `app/schemas.py`
2. Добавьте соответствующие селекторы в `ZakupkiParser`
3. Обновите логику парсинга в методе `parse()`