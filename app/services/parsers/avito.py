from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from typing import List
from bs4 import BeautifulSoup


class AvitoParser(BaseParser):
    domain = "avito.ru"
    
    def should_handle(self, url: str) -> bool:
        return "avito.ru" in url

    # Селекторы для поиска элементов внутри HTML
    selectors = {
        # Ищем все div, у которых data-marker начинается с "review("
        "container": "div[data-marker^='review(']",

        "text": "[data-marker$='/text-section/text']",
        "author": "[data-marker$='/header/title']",
        "date_block": "[data-marker$='/header/subtitle']",
        "rating_meta": "meta[itemprop='ratingValue']"
    }

    def parse(self, html: str, url: str) -> List[ReviewItem]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # 1. Находим все контейнеры отзывов
        containers = soup.select(self.selectors["container"])

        for card in containers:
            # --- Извлечение Текста ---
            text_tag = card.select_one(self.selectors["text"])
            review_text = text_tag.get_text(strip=True) if text_tag else None

            # Если текста нет (бывает только оценка), пропускаем или пишем дефолт
            if not review_text:
                continue

            # --- Извлечение Автора ---
            author_tag = card.select_one(self.selectors["author"])
            author_name = author_tag.get_text(strip=True) if author_tag else "Аноним"

            # --- Извлечение Рейтинга (из meta тега) ---
            rating_tag = card.select_one(self.selectors["rating_meta"])
            rating_value = None
            if rating_tag and rating_tag.has_attr("content"):
                rating_value = rating_tag["content"]  # Вернет строку "5" или "4"

            # --- Извлечение Даты ---
            # Дата приходит в формате "12 ноября 2025 · Арендодатель"
            # Нам нужно взять всё до точки с запятой или другого разделителя
            date_tag = card.select_one(self.selectors["date_block"])
            date_str = None
            if date_tag:
                raw_date = date_tag.get_text(strip=True)
                # Разделяем по символу '·' (это спецсимвол, который использует Авито)
                if "·" in raw_date:
                    date_str = raw_date.split("·")[0].strip()
                else:
                    date_str = raw_date

            results.append(ReviewItem(
                text=review_text,
                author=author_name,
                rating=rating_value,
                # Можно добавить поле date в ReviewItem, если расширить схему
                # date=date_str
            ))

        return results
