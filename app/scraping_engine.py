from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import logging
from datetime import datetime
import os
from fastapi import HTTPException

class ScrapingEngine:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.binary_location = os.getenv("GOOGLE_CHROME_BIN")
        self.chrome_options.add_argument("--disable-gpu")

    async def scrape_google_maps(self, config):
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(config['target_url'])
            await asyncio.sleep(5)  # Wait for dynamic content
            
            data = {}
            for field, selector in config['selectors'].items():
                try:
                    element = driver.find_element_by_css_selector(selector)
                    data[field] = element.text
                except:
                    data[field] = None
            
            return data
            
        except Exception as e:
            logging.error(f"Error scraping Google Maps: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if driver:
                driver.quit()

    async def scrape_news(self, config):
        async with aiohttp.ClientSession() as session:
            async with session.get(config['target_url']) as response:
                html = await response.text()
                
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        for article in soup.select(config['selectors']['article']):
            articles.append({
                'title': article.select_one(config['selectors']['title']).text.strip(),
                'content': article.select_one(config['selectors']['content']).text.strip(),
                'date': article.select_one(config['selectors']['date']).text.strip(),
            })
        
        return articles

    async def scrape_custom(self, config):
        driver = webdriver.Chrome(options=self.chrome_options)
        try:
            driver.get(config['target_url'])
            results = {}
            
            for field, selector in config['selectors'].items():
                try:
                    elements = driver.find_elements_by_css_selector(selector)
                    results[field] = [el.text for el in elements]
                except Exception as e:
                    logging.error(f"Error extracting {field}: {str(e)}")
            
            return results
        finally:
            driver.quit()

scraping_engine = ScrapingEngine() 