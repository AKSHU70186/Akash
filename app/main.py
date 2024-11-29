from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": str(e)}
        )

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    try:
        return templates.TemplateResponse("test.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": str(e)}
        )

@app.post("/scrape")
async def scrape(url: str = Form(...), scraper_type: str = Form(...)):
    try:
        logger.info(f"Scraping request received for URL: {url}, Type: {scraper_type}")
        
        if scraper_type == "google_maps":
            config = {
                'target_url': url,
                'selectors': {
                    'name': 'h1.DUwDvf',
                    'address': 'div.rogA2c',
                    'rating': 'div.F7nice span.ceNzKf',
                    'reviews': 'div.F7nice span.HHrUdb',
                    'phone': 'div[data-tooltip="Copy phone number"]',
                    'website': 'div[data-tooltip="Open website"]'
                }
            }
            data = await scraping_engine.scrape_google_maps(config)
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