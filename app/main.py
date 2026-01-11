from fastapi import FastAPI, HTTPException
from app.schemas import ScrapeRequest, ScrapeResponse
from app.scrapper import fetch_reviews

app = FastAPI(
    title="Review Aggregator API",
    version="0.1.0"
)


@app.get("/ping")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "service": "running"}


@app.post("/api/v1/extract-reviews", response_model=ScrapeResponse)
async def extract_reviews_endpoint(request: ScrapeRequest):
    """
    Принимает URL, парсит страницу и возвращает найденные текстовые блоки.
    """
    try:
        url_str = str(request.url)
        reviews = await fetch_reviews(url_str)

        return ScrapeResponse(
            source_url=url_str,
            reviews_count=len(reviews),
            reviews=reviews
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
