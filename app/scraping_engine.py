import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import asyncio
from dateutil import parser
import pytz

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # Set timezone to IST
        self.timezone = pytz.timezone('Asia/Kolkata')

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
                    'date': ['time', 'span.date', 'div.date-time', 'span.datetime'],
                    'summary': ['p.preview', 'div.preview', 'p:not([class])']
                },
                'date_formats': [
                    '%B %d, %Y %I:%M %p',
                    '%B %d, %Y',
                    'Updated: %B %d, %Y %I:%M %p',
                    'Published: %B %d, %Y %I:%M %p',
                    '%d %B %Y, %I:%M %p',
                    '%d %B %Y'
                ]
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
                    'date': ['span.date', 'time', 'div.date-info'],
                    'summary': ['p.content', 'div.content']
                },
                'date_formats': [
                    '%b %d, %Y %I:%M %p',
                    '%b %d, %Y',
                    '%d %b %Y, %I:%M %p',
                    'Posted on %b %d, %Y',
                    'Last updated: %b %d, %Y %I:%M %p'
                ]
            },
            'shiksha.com': {
                'name': 'Shiksha',
                'base_url': 'https://www.shiksha.com',
                'education_url': 'https://www.shiksha.com/news',
                'selectors': {
                    'article_wrapper': 'div.news-tuple, div.nws-tuple',
                    'title': 'h2.news-title a, div.tuple-title a',
                    'link': 'h2.news-title a, div.tuple-title a',
                    'description': 'div.news-snippet, div.tuple-desc',
                    'date': ['div.date-tuple', 'span.date-info', 'meta[property="article:published_time"]'],
                    'summary': ['div.news-snippet', 'div.tuple-desc']
                },
                'date_formats': [
                    '%d %b %Y',
                    '%d %b %Y, %I:%M %p',
                    '%Y-%m-%dT%H:%M:%S%z',
                    'Posted: %d %b %Y',
                    'Last Updated: %d %b %Y, %I:%M %p'
                ]
            },
            'timesofindia.indiatimes.com': {
                'name': 'Times of India',
                'base_url': 'https://timesofindia.indiatimes.com',
                'education_url': 'https://timesofindia.indiatimes.com/education',
                'selectors': {
                    'article_wrapper': 'div.list5.clearfix article, div.education-story',
                    'title': 'span.w_tle a, h3 a',
                    'link': 'span.w_tle a, h3 a',
                    'description': 'p.desc',
                    'date': ['span.date', 'time', 'meta[property="article:published_time"]'],
                    'summary': ['p.desc', 'div.synopsis']
                },
                'date_formats': [
                    '%b %d, %Y, %I:%M %p IST',
                    '%d %b %Y, %I:%M %p',
                    '%Y-%m-%dT%H:%M:%S%z',
                    'Updated: %b %d, %Y, %I:%M %p IST',
                    '%d %b %Y'
                ]
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
                            # Rotate User-Agent on 403
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

    def parse_date(self, date_str: str, formats: List[str]) -> Optional[str]:
        """Parse date string to formatted datetime"""
        if not date_str:
            return None

        # Clean the date string
        date_str = re.sub(r'\s+', ' ', date_str.strip())
        
        # Remove common prefixes
        date_str = re.sub(r'^(Updated:|Published:|Posted:|Last Updated:|Updated on:|Published on:)\s*', '', date_str)
        
        # Try parsing with dateutil first
        try:
            parsed_date = parser.parse(date_str, fuzzy=True)
            if parsed_date.tzinfo is None:
                parsed_date = self.timezone.localize(parsed_date)
            return parsed_date.strftime('%Y-%m-%d %I:%M %p IST')
        except:
            # Try specific formats
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    parsed_date = self.timezone.localize(parsed_date)
                    return parsed_date.strftime('%Y-%m-%d %I:%M %p IST')
                except:
                    continue
        
        return date_str

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

                    # Extract summary
                    summary = self.extract_text_from_selectors(article, config['selectors']['summary'])

                    # Extract date
                    date_str = None
                    for date_selector in config['selectors']['date']:
                        date_elem = article.select_one(date_selector)
                        if date_elem:
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