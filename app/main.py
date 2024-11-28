from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import logging
import os
from .routers import scrapers
from .middleware.rate_limiter import RateLimiter
from .proxy_manager import ProxyRotator
from .queue_manager import queue_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(title="Web Scraper")

# Ensure directories exist
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Initialize components
rate_limiter = RateLimiter()
proxy_rotator = ProxyRotator()

# Include routers
app.include_router(scrapers.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse(
            "test.html",
            {
                "request": request,
            }
        )
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-scrape")
async def test_scrape(url: str = Form(...), scraper_type: str = Form(...)):
    try:
        logger.info(f"Received scraping request for URL: {url} with type: {scraper_type}")
        
        # For testing, return dummy data
        return {
            "status": "success",
            "data": {
                "url": url,
                "type": scraper_type,
                "sample_data": "Test data scraped successfully"
            }
        }
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Error handler for 500 Internal Server Error
@app.exception_handler(500)
async def internal_server_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": str(exc.detail)
        },
        status_code=500
    )

# Make sure this is at the end of the file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 