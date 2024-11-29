import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import json
import asyncio

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        # Detailed configuration for each supported website
        self.site_configs = {
            'indianexpress.com': {
                'name': 'Indian Express',
                'base_url': 'https://indianexpress.com',
                'education_url': 'https://indianexpress.com/section/education/',
                'selectors': {
                    'article_wrapper': 'div.article-list article, div.nation div[class*="article"]',
                    'title': ['h2.title', 'h2 a', 'h3 a'],
                    'link': ['h2.title a', 'h2 a', 'h3 a'],
                    'description': ['p.preview', 'h4', 'p:not([class])'],
                    'date': ['time', 'span.date', 'div.date'],
                    'image': ['img.lazy-load-image', 'img.lazy']
                },
                'pagination': '?page={}'
            },
            'careers360.com': {
                'name': 'Careers360',
                'base_url': 'https://news.careers360.com',
                'education_url': 'https://news.careers360.com',
                'selectors': {
                    'article_wrapper': 'div.newsListBlock, div.article-list',
                    'title': ['h3.headingText', 'h2.title'],
                    'link': ['a.click-able', 'h3.headingText a'],
                    'description': ['p.content', 'div.content'],
                    'date': ['span.date', 'time'],
                    'image': ['img.lazy']
                },
                'pagination': '?page={}'
            },
            'timesofindia.indiatimes.com': {
                'name': 'Times of India',
                'base_url': 'https://timesofindia.indiatimes.com',
                'education_url': 'https://timesofindia.indiatimes.com/education',
                'selectors': {
                    'article_wrapper': 'div.list5.clearfix, div.main-content article',
                    'title': ['span.w_tle', 'figcaption a', 'h3 a'],
                    'link': ['a[href*="/education/"]', 'figcaption a'],
                    'description': ['p.desc', 'figcaption p'],
                    'date': ['span.date', 'time'],
                    'image': ['img[src*="photo"]']
                },
                'pagination': '/page/{}'
            },
            'shiksha.com': {
                'name': 'Shiksha',
                'base_url': 'https://www.shiksha.com',
                'education_url': 'https://www.shiksha.com/news',
                'selectors': {
                    'article_wrapper': 'div.news-tuple',
                    'title': ['h2.news-title', 'div.news-title'],
                    'link': ['a.tuple-link'],
                    'description': ['div.news-snippet'],
                    'date': ['div.date-tuple'],
                    'image': ['img.lazy']
                },
                'pagination': '?page={}'
            }
        }

    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch URL content with retry mechanism"""
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 403:
                            # Try with different headers
                            self.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                            continue
                        else:
                            logging.error(f"Failed to fetch {url}: Status {response.status}")
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)
        return None

    def get_site_config(self, url: str) -> Optional[Dict]:
        """Get configuration for given URL"""
        domain = urlparse(url).netloc
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

    def extract_element(self, article: BeautifulSoup, selectors: List[str], attr: Optional[str] = None) -> Optional[str]:
        """Extract element using multiple possible selectors"""
        for selector in selectors:
            element = article.select_one(selector)
            if element:
                if attr:
                    return element.get(attr)
                return self.clean_text(element.get_text())
        return None

    async def scrape_website(self, url: str, max_pages: int = 3) -> List[Dict]:
        """Main scraping function with pagination support"""
        try:
            config = self.get_site_config(url)
            if not config:
                raise ValueError("Unsupported website")

            all_articles = []
            base_url = config['base_url']

            # Scrape multiple pages
            for page in range(1, max_pages + 1):
                try:
                    page_url = url if page == 1 else f"{url}{config['pagination'].format(page)}"
                    html = await self.fetch_with_retry(page_url)
                    if not html:
                        continue

                    soup = BeautifulSoup(html, 'html.parser')
                    articles = soup.select(config['selectors']['article_wrapper'])

                    for article in articles:
                        try:
                            # Extract article data
                            title = self.extract_element(article, config['selectors']['title'])
                            if not title:
                                continue

                            link = self.extract_element(article, config['selectors']['link'], 'href')
                            if link:
                                if not link.startswith('http'):
                                    link = urljoin(base_url, link)

                            description = self.extract_element(article, config['selectors']['description'])
                            date = self.extract_element(article, config['selectors']['date'])
                            image = self.extract_element(article, config['selectors']['image'], 'src')

                            article_data = {
                                'title': title,
                                'link': link,
                                'description': description,
                                'date': date,
                                'image': image,
                                'source': config['name']
                            }

                            # Only add unique articles
                            if article_data not in all_articles:
                                all_articles.append(article_data)

                        except Exception as e:
                            logging.error(f"Error extracting article: {str(e)}")
                            continue

                except Exception as e:
                    logging.error(f"Error scraping page {page}: {str(e)}")
                    continue

            return all_articles

        except Exception as e:
            logging.error(f"Scraping error: {str(e)}")
            raise

# Ensure scraping_engine is defined
scraping_engine = ScrapingEngine()