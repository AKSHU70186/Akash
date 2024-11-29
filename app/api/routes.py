from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from ..scraping_engine import scraping_engine

router = APIRouter()

class ScrapingResponse(BaseModel):
    status: str
    data: List[dict]
    message: Optional[str] = None

@router.get("/scrape/education", response_model=ScrapingResponse)
async def scrape_education_news(url: HttpUrl):
    """Scrape education news from supported websites"""
    try:
        data = await scraping_engine.scrape_website(str(url))
        return {
            "status": "success",
            "data": data,
            "message": f"Successfully scraped {len(data)} articles"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape/google-maps", response_model=ScrapingResponse)
async def scrape_google_maps(place_id: str = Query(..., description="Google Maps Place ID")):
    """Scrape reviews from Google Maps"""
    try:
        data = await scraping_engine.scrape_google_maps_reviews(place_id)
        return {
            "status": "success",
            "data": data,
            "message": f"Successfully scraped {len(data)} reviews"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-sites")
async def get_supported_sites():
    """Get list of supported websites"""
    sites = []
    for domain, config in scraping_engine.site_configs.items():
        sites.append({
            'name': config['name'],
            'url': config['education_url']
        })
    return {
        "status": "success",
        "data": sites
    } 