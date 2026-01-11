from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from app.schemas import ReviewItem
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_reviews(url: str) -> list[ReviewItem]:
    logger.info(f"Starting scrape for: {url}")

    async with async_playwright() as p:
        # Запускаем headless Chrome
        browser = await p.chromium.launch(headless=True)

        # Создаем контекст с User-Agent, похожим на реальный
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # Переходим на страницу и ждем загрузки DOM (макс 30 сек)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # В будущем здесь будет скроллинг страницы

            # Забираем HTML
            content = await page.content()

        except Exception as e:
            logger.error(f"Playwright error: {e}")
            await browser.close()
            raise e

        await browser.close()

    # Парсинг HTML через BeautifulSoup (это быстрее и надежнее)
    soup = BeautifulSoup(content, "html.parser")
    reviews = []

    # --- ЛОГИКА MVP ---
    # Так как сайты разные, для теста MVP мы просто ищем параграфы <p>,
    # которые длиннее 20 символов, имитируя отзывы.
    # В Спринте 2 здесь будет паттерн "Стратегия" под разные сайты.

    potential_reviews = soup.find_all("p")

    for p in potential_reviews[:10]:  # Берем первые 10
        text = p.get_text(strip=True)
        if len(text) > 30:
            reviews.append(ReviewItem(text=text))

    logger.info(f"Found {len(reviews)} potential reviews")
    return reviews
