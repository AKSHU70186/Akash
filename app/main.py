from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from .scraping_engine import scraping_engine
from .exporters import DataExporter
from datetime import datetime

app = FastAPI()

# CORS and Static files configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create exports directory if it doesn't exist
os.makedirs("exports", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape")
async def scrape(request: Request, url: str = Form(...)):
    try:
        config = {'target_url': url}
        data = await scraping_engine.scrape_news(config)
        
        # Store the scraped data for export
        request.app.state.last_scraped_data = data
        
        return JSONResponse({
            "status": "success",
            "data": {
                "url": url,
                "scraped_data": data
            }
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/export/{format}")
async def export_data(format: str):
    try:
        if not hasattr(app.state, 'last_scraped_data'):
            raise HTTPException(status_code=400, detail="No data available for export")

        data = app.state.last_scraped_data
        exporter = DataExporter(data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"news_data_{timestamp}"

        if format == "excel":
            filepath = await exporter.to_excel(filename)
            return FileResponse(
                filepath,
                filename=f"{filename}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif format == "csv":
            filepath = await exporter.to_csv(filename)
            return FileResponse(
                filepath,
                filename=f"{filename}.csv",
                media_type="text/csv"
            )
        elif format == "json":
            filepath = await exporter.to_json(filename)
            return FileResponse(
                filepath,
                filename=f"{filename}.json",
                media_type="application/json"
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
