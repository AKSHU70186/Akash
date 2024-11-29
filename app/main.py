from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from .scraping_engine import scraping_engine

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="Education News Scraper")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/scrape")
async def scrape_news(url: str):
    try:
        logging.info(f"Starting scraping for URL: {url}")
        results = await scraping_engine.scrape_website(url)
        
        if not results:
            logging.warning("No results found")
            return JSONResponse({
                "status": "warning",
                "message": "No articles found",
                "data": []
            })

        logging.info(f"Successfully scraped {len(results)} articles")
        return JSONResponse({
            "status": "success",
            "message": f"Successfully scraped {len(results)} articles",
            "data": results
        })

    except Exception as e:
        logging.error(f"Scraping error: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": f"Error while scraping: {str(e)}",
            "data": []
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Your existing routes remain the same
