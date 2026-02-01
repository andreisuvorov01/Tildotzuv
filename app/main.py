from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import ScrapeRequest, ScrapeResponse
from app.core.browser import browser_manager
from app.services.scraper_engine import ScraperEngine


# LIFESPAN - новый способ управления событиями запуска/остановки в FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: запускаем браузер
    await browser_manager.startup()
    yield
    # Shutdown: гасим браузер
    await browser_manager.shutdown()


app = FastAPI(title="Review Aggregator API", lifespan=lifespan)

# Добавляем CORS для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/extract-reviews", response_model=ScrapeResponse)
async def extract_reviews_endpoint(request: ScrapeRequest):
    engine = ScraperEngine()

    try:
        url_str = str(request.url)
        print(f"Processing URL: {url_str}")
        print(f"Filters: {request.filters}")
        
        reviews = await engine.run(url_str, request.filters)

        return ScrapeResponse(
            source_url=url_str,
            reviews_count=len(reviews),
            reviews=reviews,
            applied_filters=request.filters
        )
    except ValueError as e:
        print(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))