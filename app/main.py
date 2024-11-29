from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .scraping_engine import scraping_engine
import logging
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape")
async def scrape(url: str = Form(...), scraper_type: str = Form(...)):
    try:
        logger.info(f"Scraping request received for URL: {url}, Type: {scraper_type}")
        
        config = {
            'target_url': url,
            'selectors': get_selectors_for_type(scraper_type)
        }
        
        if scraper_type == "google_maps":
            data = await scraping_engine.scrape_google_maps(config)
        elif scraper_type == "e_commerce":
            data = await scraping_engine.scrape_custom(config)
        elif scraper_type == "news":
            data = await scraping_engine.scrape_news(config)
        else:
            raise HTTPException(status_code=400, detail=f"Scraper type '{scraper_type}' not supported")

        return JSONResponse({
            "status": "success",
            "data": {
                "url": url,
                "type": scraper_type,
                "scraped_data": data
            }
        })
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

def get_selectors_for_type(scraper_type: str) -> dict:
    selectors = {
        "google_maps": {
            'name': 'h1.DUwDvf',
            'address': 'div.rogA2c',
            'rating': 'div.F7nice span.ceNzKf',
            'reviews': 'div.F7nice span.HHrUdb',
            'phone': 'div[data-tooltip="Copy phone number"]',
            'website': 'div[data-tooltip="Open website"]'
        },
        "e_commerce": {
            'name': 'h1.product-title',
            'price': 'span.price',
            'description': 'div.product-description',
            'images': 'img.product-image'
        },
        "news": {
            'article': 'article',
            'title': 'h2.title',
            'content': 'div.content',
            'date': 'time.published'
        }
    }
    return selectors.get(scraper_type, {}) 