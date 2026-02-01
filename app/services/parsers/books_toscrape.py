from app.services.parsers.base import BaseParser
from app.schemas import ReviewItem
from typing import List


class BooksToScrapeParser(BaseParser):

    def should_handle(self, url: str) -> bool:
        return "books.toscrape.com" in url

    def parse(self, html_content: str, url: str) -> List[ReviewItem]:
        soup = self._get_soup(html_content)
        results = []

        # На этом сайте товары лежат в <article class="product_pod">
        cards = soup.select("article.product_pod")

        for card in cards:
            # Извлекаем название книги
            title_tag = card.select_one("h3 a")
            title = title_tag.attrs["title"] if title_tag else "No Title"

            # Извлекаем рейтинг (он в классе, например "star-rating Three")
            rating_tag = card.select_one(".star-rating")
            rating_classes = rating_tag.attrs.get("class", []) if rating_tag else []
            # Берем последнее слово класса ("Three", "Four") как рейтинг
            rating = rating_classes[-1] if len(rating_classes) > 1 else "Unknown"

            # Извлекаем цену
            price = card.select_one(".price_color")
            price_text = price.get_text(strip=True) if price else ""

            # Формируем объект отзыва (мапим книгу на отзыв для теста)
            results.append(ReviewItem(
                text=f"Book: {title}. Price: {price_text}",
                author="BooksToScrape",
                rating=rating
            ))

        return results
