from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from .scraping_engine import scraping_engine
from .exporters import DataExporter
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="Education News Scraper")

# Configure logging
logging.basicConfig(level=logging.INFO)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create exports directory
os.makedirs("exports", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/supported-sites")
async def get_supported_sites():
    """Get list of supported websites"""
    sites = []
    for domain, config in scraping_engine.site_configs.items():
        sites.append({
            'name': config['name'],
            'url': config['education_url']
        })
    return JSONResponse({
        "status": "success",
        "data": sites
    })

@app.post("/scrape")
async def scrape(request: Request, url: str = Form(...)):
    """Scrape website content"""
    try:
        # Validate URL
        if not url.startswith('http'):
            url = f"https://{url}"

        # Scrape the website
        data = await scraping_engine.scrape_website(url)
        
        if not data:
            return JSONResponse({
                "status": "warning",
                "message": "No articles found",
                "data": {"url": url, "scraped_data": []}
            })

        # Store data for export
        request.app.state.last_scraped_data = data
        
        return JSONResponse({
            "status": "success",
            "data": {
                "url": url,
                "scraped_data": data
            }
        })

    except ValueError as ve:
        return JSONResponse({
            "status": "error",
            "message": str(ve)
        }, status_code=400)
    except Exception as e:
        logging.error(f"Scraping error: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": "Failed to scrape website"
        }, status_code=500)

@app.get("/export/{format}")
async def export_data(format: str):
    """Export scraped data"""
    try:
        if not hasattr(app.state, 'last_scraped_data'):
            raise HTTPException(status_code=400, detail="No data available for export")

        data = app.state.last_scraped_data
        exporter = DataExporter(data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_data_{timestamp}"

        if format == "csv":
            filepath = await exporter.to_csv(filename)
            return FileResponse(filepath, filename=f"{filename}.csv", media_type="text/csv")
        elif format == "json":
            filepath = await exporter.to_json(filename)
            return FileResponse(filepath, filename=f"{filename}.json", media_type="application/json")
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Make sure the app is properly exposed
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
