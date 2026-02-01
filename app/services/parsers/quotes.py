from app.services.parsers.base import BaseParser
class QuotesParser(BaseParser):
    # 1. На какой домен реагировать
    domain = "quotes.toscrape.com"

    # 2. CSS селекторы (словарь)
    selectors = {
        "container": "div.quote",  # Блок одной цитаты
        "text": "span.text",  # Сам текст
        "author": "small.author",  # Автор
        "rating": None  # Рейтинга тут нет
    }
