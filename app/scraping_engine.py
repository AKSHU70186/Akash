from bs4 import BeautifulSoup
import aiohttp
import logging
from fastapi import HTTPException
import json
from datetime import datetime
import re

class ScrapingEngine:
    def __init__(self):
        self.website_configs = {
            'careers360': {
                'url': 'https://news.careers360.com',
                'selectors': {
                    'articles': 'div.newsListBlock',
                    'title': 'h3.headingText',
                    'link': 'a',
                    'description': 'p.content',
                    'date': 'span.date'
                }
            }
        }

    async def fetch_html(self, url: str) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise HTTPException(status_code=response.status, detail=f"Failed to fetch {url}")
        except Exception as e:
            logging.error(f"Error fetching URL {url}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")

    async def scrape_news(self, config: dict) -> list:
        try:
            site_config = self.website_configs['careers360']
            html = await self.fetch_html(site_config['url'])
            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            # Find all article elements
            article_elements = soup.select(site_config['selectors']['articles'])
            
            for article in article_elements:
                try:
                    # Extract title
                    title_element = article.select_one(site_config['selectors']['title'])
                    title = title_element.text.strip() if title_element else None

                    # Extract link
                    link_element = article.select_one(site_config['selectors']['link'])
                    link = link_element['href'] if link_element else None
                    if link and not link.startswith('http'):
                        link = site_config['url'] + link

                    # Extract description
                    desc_element = article.select_one(site_config['selectors']['description'])
                    description = desc_element.text.strip() if desc_element else None

                    # Extract date
                    date_element = article.select_one(site_config['selectors']['date'])
                    date = date_element.text.strip() if date_element else None

                    if title and link:  # Only add if we have at least title and link
                        article_data = {
                            'title': title,
                            'link': link,
                            'description': description,
                            'date': date,
                            'source': 'Careers360'
                        }
                        articles.append(article_data)

                except Exception as e:
                    logging.error(f"Error parsing article: {str(e)}")
                    continue

            if not articles:
                logging.warning("No articles found")
                return []

            return articles

        except Exception as e:
            logging.error(f"Error scraping news: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

scraping_engine = ScrapingEngine() 