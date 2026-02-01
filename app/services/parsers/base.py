from abc import ABC
from bs4 import BeautifulSoup
from app.schemas import ReviewItem
from typing import List, Optional


class BaseParser(ABC):
    domain: str = ""
    selectors: dict = {}

    def should_handle(self, url: str) -> bool:
        return self.domain in url

    # ЭТОТ МЕТОД ОДИН ДЛЯ ВСЕХ. ЕГО НЕ НАДО ПЕРЕПИСЫВАТЬ.
    def parse(self, html: str, url: str) -> List[ReviewItem]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Получаем селектор контейнера из конфига дочернего класса
        container_sel = self.selectors.get("container")
        if not container_sel:
            return []

        cards = soup.select(container_sel)

        for card in cards:
            # Универсальное извлечение текста
            text = self._get_text(card, self.selectors.get("text"))
            author = self._get_text(card, self.selectors.get("author"))
            rating = self._get_text(card, self.selectors.get("rating"))

            if text:
                results.append(ReviewItem(
                    text=text,
                    author=author or "Anonymous",
                    rating=rating
                ))
        return results

    def _get_text(self, soup_element, selector: Optional[str]) -> Optional[str]:
        if not selector:
            return None
        el = soup_element.select_one(selector)
        return el.get_text(strip=True) if el else None
