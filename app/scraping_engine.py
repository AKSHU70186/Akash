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
            'indianexpress': {
                'domain': 'indianexpress.com',
                'selectors': {
                    'articles': '.article-list article, .nation article, div.articles article',
                    'title': 'h2, h3, .title',
                    'link': 'a',
                    'image': 'img',
                    'description': '.description, .synopsis, p:not(.date)',
                    'date': '.date, time, .time-stamp'
                }
            },
            'careers360': {
                'domain': 'careers360.com',
                'selectors': {
                    'articles': '.news-article, .article-item, .news-card',
                    'title': '.title, h2, h3',
                    'link': 'a',
                    'image': 'img',
                    'description': '.description, .excerpt, .summary',
                    'date': '.date, .published-date'
                }
            },
            'shiksha': {
                'domain': 'shiksha.com',
                'selectors': {
                    'articles': '.news-tuple, .article-box, .news-item',
                    'title': 'h2, .heading, .title',
                    'link': 'a',
                    'image': 'img',
                    'description': '.description, .snippet',
                    'date': '.date, .timestamp'
                }
            },
            'ndtv': {
                'domain': 'ndtv.com',
                'selectors': {
                    'articles': '.news_item, .article-item, .story_box',
                    'title': 'h2, .headline',
                    'link': 'a',
                    'image': 'img',
                    'description': '.description, .intro',
                    'date': '.posted-date, .time'
                }
            },
            'timesofindiaindiatimes': {
                'domain': 'timesofindia.indiatimes.com',
                'selectors': {
                    'articles': '.article-box, .news-card',
                    'title': '.title, h2',
                    'link': 'a',
                    'image': 'img',
                    'description': '.summary, .synopsis',
                    'date': '.date, .time-stamp'
                }
            }
        }

    def get_website_config(self, url):
        for site_key, config in self.website_configs.items():
            if config['domain'] in url:
                return site_key, config
        return None, None

    async def scrape_news(self, config):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }

            url = config['target_url']
            site_key, site_config = self.get_website_config(url)

            if not site_config:
                raise HTTPException(status_code=400, detail="Unsupported website")

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=400, detail="Failed to fetch the webpage")
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            # Find all article elements using site-specific selectors
            selectors = site_config['selectors']
            article_elements = soup.select(selectors['articles'])

            for article in article_elements:
                try:
                    # Extract title
                    title_element = article.select_one(selectors['title'])
                    if not title_element:
                        continue

                    title = title_element.get_text(strip=True)

                    # Extract link
                    link_element = article.select_one(selectors['link'])
                    link = link_element.get('href', '') if link_element else ''

                    # Ensure link is absolute
                    if link and not link.startswith('http'):
                        link = f"https://{site_config['domain']}" + link

                    # Extract image
                    img_element = article.select_one(selectors['image'])
                    image_url = None
                    if img_element:
                        image_url = (img_element.get('data-lazy-src') or 
                                   img_element.get('data-src') or 
                                   img_element.get('src'))

                    # Extract description
                    desc_element = article.select_one(selectors['description'])
                    description = desc_element.get_text(strip=True) if desc_element else None

                    # Extract date
                    date_element = article.select_one(selectors['date'])
                    date = None
                    if date_element:
                        date_text = date_element.get_text(strip=True)
                        # Try to parse and standardize the date format
                        try:
                            # Add your date parsing logic here
                            date = date_text
                        except:
                            date = date_text

                    if title and link:  # Only add if we have at least title and link
                        article_data = {
                            'title': title,
                            'link': link,
                            'image_url': image_url,
                            'description': description,
                            'date': date,
                            'source': site_config['domain']
                        }
                        articles.append(article_data)

                except Exception as e:
                    logging.error(f"Error parsing article: {str(e)}")
                    continue

            return articles

        except Exception as e:
            logging.error(f"Error scraping news: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

scraping_engine = ScrapingEngine() 