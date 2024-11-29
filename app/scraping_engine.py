import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import asyncio

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        self.site_configs = {
            'indianexpress.com': {
                'name': 'Indian Express',
                'base_url': 'https://indianexpress.com',
                'education_url': 'https://indianexpress.com/section/education/',
                'selectors': {
                    'article_wrapper': 'div.article-list article, div.nation div[class*="article"]',
                    'title': 'h2.title a, h3 a',
                    'link': 'h2.title a, h3 a',
                    'description': ['p.preview', 'div.preview', 'p:not([class])', 'div.synopsis'],
                    'date': 'time, span.date',
                    'summary': ['p.preview', 'div.preview', 'p:not([class])', 'div.synopsis']
                }
            }
        }

    async def fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch and extract full article content"""
        try:
            html = await self.fetch_with_retry(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                # Find article content
                content = soup.select_one('div.article-content, div.full-details')
                if content:
                    # Extract first few paragraphs
                    paragraphs = content.select('p')
                    summary = ' '.join([p.get_text().strip() for p in paragraphs[:2]])
                    return self.clean_text(summary)
            return None
        except Exception as e:
            logging.error(f"Error fetching article content: {str(e)}")
            return None

    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch URL content with retry mechanism"""
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)
        return None

    def get_site_config(self, url: str) -> Optional[Dict]:
        """Get configuration for given URL"""
        domain = urlparse(url).netloc.lower()
        return next((config for site, config in self.site_configs.items() if site in domain), None)

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters
        text = re.sub(r'[\n\r\t]', '', text)
        return text

    def extract_text_from_selectors(self, article: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Try multiple selectors to extract text"""
        for selector in selectors:
            element = article.select_one(selector)
            if element:
                return self.clean_text(element.get_text())
        return None

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

                    # Extract summary from article preview
                    summary = self.extract_text_from_selectors(article, config['selectors']['summary'])
                    
                    # If no summary in preview, fetch from article page
                    if not summary and link:
                        summary = await self.fetch_article_content(link)

                    # Extract date
                    date_elem = article.select_one(config['selectors']['date'])
                    date = self.clean_text(date_elem.get_text()) if date_elem else ""

                    # Only add articles with at least a title
                    if title:
                        article_data = {
                            'title': title,
                            'link': link,
                            'summary': summary if summary else "Click to read more...",
                            'date': date,
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