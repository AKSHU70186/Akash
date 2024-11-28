from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from enum import Enum

class ScraperType(str, Enum):
    GOOGLE_MAPS = "google_maps"
    NEWS = "news"
    E_COMMERCE = "e_commerce"
    CUSTOM = "custom"

class ScraperCreate(BaseModel):
    name: str
    type: ScraperType
    target_url: HttpUrl
    selectors: Dict[str, str]
    schedule: Optional[str]  # Cron expression
    proxy_config: Optional[Dict]

class ScraperRun(BaseModel):
    scraper_id: str
    parameters: Optional[Dict]

class ScrapedData(BaseModel):
    url: str
    type: ScraperType
    data: Dict
    timestamp: str