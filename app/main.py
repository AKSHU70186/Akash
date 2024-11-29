from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from .scraping_engine import scraping_engine
import os

app = FastAPI()

@app.post("/scrape")
async def scrape(url: str = Form(...)):
    try:
        config = {
            'target_url': url
        }
        
        data = await scraping_engine.scrape_news(config)
        
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 