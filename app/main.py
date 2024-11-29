from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
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