from fastapi import APIRouter, Depends
from typing import List
from ..models import *
from ..auth import get_current_user

router = APIRouter()

@router.get("/scrapers")
async def list_scrapers(user: str = Depends(get_current_user)):
    """List all scrapers for the current user"""
    scrapers = await db.scrapers.find({"user": user}).to_list(None)
    return scrapers

@router.get("/scrapers/{scraper_id}/runs")
async def list_runs(scraper_id: str, user: str = Depends(get_current_user)):
    """List all runs for a specific scraper"""
    runs = await db.runs.find({"scraper_id": scraper_id}).to_list(None)
    return runs

@router.get("/runs/{run_id}/results")
async def get_results(run_id: str, user: str = Depends(get_current_user)):
    """Get results for a specific run"""
    results = await db.results.find_one({"run_id": run_id})
    return results 