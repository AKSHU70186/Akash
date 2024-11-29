import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse, quote
import asyncio
from dateutil import parser
import pytz
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        self.timezone = pytz.timezone('Asia/Kolkata')
        
        # Configure Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')

        # Website configurations
        self.site_configs = {
            'indianexpress.com': {
                'name': 'Indian Express',
                'base_url': 'https://indianexpress.com',
                'education_url': 'https://indianexpress.com/section/education/',
                'selectors': {
                    'article_wrapper': 'div.article-list article, div.nation div[class*="article"]',
                    'title': 'h2.title a, h3 a',
                    'link': 'h2.title a, h3 a',
                    'description': ['p.preview', 'div.preview', 'p:not([class])'],
                    'date': ['time', 'span.date'],
                    'summary': ['p.preview', 'div.preview', 'p:not([class])']
                }
            },
            'careers360.com': {
                'name': 'Careers360',
                'base_url': 'https://news.careers360.com',
                'education_url': 'https://news.careers360.com',
                'selectors': {
                    'article_wrapper': 'div.newsListBlock, article.news_article',
                    'title': 'h3.headingText a, h2.title a',
                    'link': 'h3.headingText a, h2.title a',
                    'description': 'p.content, div.content',
                    'date': 'span.date, time'
                }
            },
            'ndtv.com': {
                'name': 'NDTV Education',
                'base_url': 'https://www.ndtv.com',
                'education_url': 'https://www.ndtv.com/education',
                'selectors': {
                    'article_wrapper': 'div.news_item, div.article-item',
                    'title': 'h2 a',
                    'link': 'h2 a',
                    'description': 'p.description',
                    'date': 'span.posted-date'
                }
            },
            # Add more websites as needed
        }

    async def scrape_google_maps_reviews(self, place_id: str) -> List[Dict]:
        """Scrape reviews from Google Maps"""
        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Construct Google Maps URL
            url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
            driver.get(url)
            
            # Wait for reviews to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "section-review-content"))
            )
            
            # Scroll to load more reviews
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            reviews = []
            review_elements = driver.find_elements(By.CLASS_NAME, "section-review-content")
            
            for element in review_elements:
                try:
                    review = {
                        'author': element.find_element(By.CLASS_NAME, "section-review-title").text,
                        'rating': element.find_element(By.CLASS_NAME, "section-review-stars").get_attribute("aria-label"),
                        'text': element.find_element(By.CLASS_NAME, "section-review-text").text,
                        'date': element.find_element(By.CLASS_NAME, "section-review-date").text
                    }
                    reviews.append(review)
                except Exception as e:
                    logging.error(f"Error extracting review: {str(e)}")
                    continue
            
            driver.quit()
            return reviews
            
        except Exception as e:
            logging.error(f"Error scraping Google Maps reviews: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            return []

    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Enhanced fetch with retry mechanism"""
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 403:
                            # Rotate User-Agent
                            user_agents = [
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
                                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
                                'Mozilla/5.0 (X11; Linux x86_64) Firefox/89.0'
                            ]
                            self.headers['User-Agent'] = user_agents[attempt % len(user_agents)]
                            continue
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)
        return None

    def parse_date(self, date_str: str, formats: List[str]) -> Optional[str]:
        """Parse date string to formatted datetime"""
        if not date_str:
            return None

        # Clean the date string
        date_str = re.sub(r'\s+', ' ', date_str.strip())
        
        # Try parsing with dateutil first
        try:
            # Parse the date
            parsed_date = parser.parse(date_str, fuzzy=True)
            
            # Set timezone to IST if naive
            if parsed_date.tzinfo is None:
                parsed_date = self.timezone.localize(parsed_date)
            
            # Format the date
            return parsed_date.strftime('%Y-%m-%d %I:%M %p IST')
        except:
            # Try specific formats
            for fmt in formats:
                try:
                    # Remove common prefixes
                    clean_date = re.sub(r'^(Updated:|Published:|Posted:)\s*', '', date_str)
                    parsed_date = datetime.strptime(clean_date, fmt)
                    # Set timezone to IST
                    parsed_date = self.timezone.localize(parsed_date)
                    return parsed_date.strftime('%Y-%m-%d %I:%M %p IST')
                except:
                    continue
        
        return date_str  # Return original if parsing fails

    async def scrape_website(self, url: str) -> List[Dict]:
        """Main scraping function"""
        try:
            config = self.get_site_config(url)
            if not config:
                raise ValueError(f"Unsupported website: {url}")

            html = await self.fetch_with_retry(url)
            if not html:
                raise ValueError(f"Failed to fetch content from {url}")

            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            # Find all article elements
            article_elements = soup.select(config['selectors']['article_wrapper'])
            
            for article in article_elements:
                try:
                    # Extract title and link
                    title_elem = article.select_one(config['selectors']['title'])
                    if not title_elem:
                        continue

                    title = self.clean_text(title_elem.get_text())
                    link = title_elem.get('href', '')
                    
                    # Make link absolute if it's relative
                    if link and not link.startswith('http'):
                        link = urljoin(config['base_url'], link)

                    # Extract summary
                    summary = self.extract_text_from_selectors(article, config['selectors']['summary'])
                    if not summary and link:
                        summary = await self.fetch_article_content(link)

                    # Extract and parse date
                    date_str = None
                    for date_selector in config['selectors']['date']:
                        date_elem = article.select_one(date_selector)
                        if date_elem:
                            # Check for datetime attribute first
                            date_str = (
                                date_elem.get('datetime') or 
                                date_elem.get('data-datetime') or 
                                date_elem.get_text()
                            )
                            if date_str:
                                break

                    # Parse the date
                    formatted_date = self.parse_date(date_str, config.get('date_formats', []))

                    # Only add articles with at least a title
                    if title:
                        article_data = {
                            'title': title,
                            'link': link,
                            'summary': summary if summary else "Click to read more...",
                            'published_date': formatted_date,
                            'source': config['name']
                        }
                        
                        # Avoid duplicates
                        if article_data not in articles:
                            articles.append(article_data)

                except Exception as e:
                    logging.error(f"Error extracting article: {str(e)}")
                    continue

            if not articles:
                logging.warning(f"No articles found on {url}")
                return []

            return articles

        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            raise

# Initialize scraping engine
scraping_engine = ScrapingEngine()