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
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(config['target_url']) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=400, detail="Failed to fetch the webpage")
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            # Specific selectors for Indian Express education section
            article_elements = soup.select('div.articles article, div.nation article, .article-list li')
            
            for article in article_elements:
                try:
                    # Title and Link
                    title_element = article.select_one('h2 a, h3 a, .title a')
                    if not title_element:
                        continue
                        
                    title = title_element.text.strip()
                    link = title_element.get('href', '')
                    if link and not link.startswith('http'):
                        link = 'https://indianexpress.com' + link

                    # Image
                    image_element = article.select_one('img')
                    image_url = image_element.get('data-lazy-src') or image_element.get('src') if image_element else None

                    # Date
                    date_element = article.select_one('time, .date, span.date')
                    date = date_element.text.strip() if date_element else None

                    # Description
                    desc_element = article.select_one('p.preview, .synopsis, .description')
                    description = desc_element.text.strip() if desc_element else None

                    if title:  # Only add articles that have at least a title
                        article_data = {
                            'title': title,
                            'link': link,
                            'image_url': image_url,
                            'date': date,
                            'description': description
                        }
                        articles.append(article_data)
                        
                except Exception as e:
                    logging.error(f"Error parsing article: {str(e)}")
                    continue

            return articles

        except Exception as e:
            logging.error(f"Error scraping news: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

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