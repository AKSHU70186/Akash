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
                    'description': ['p.preview', 'div.preview', 'p:not([class])', 'div.synopsis'],
                    'date': ['time', 'span.date', 'div.date-time', 'span.datetime'],
                    'summary': ['p.preview', 'div.preview', 'p:not([class])', 'div.synopsis']
                },
                'date_formats': [
                    '%B %d, %Y %I:%M %p',
                    '%B %d, %Y',
                    'Updated: %B %d, %Y %I:%M %p',
                    'Published: %B %d, %Y %I:%M %p'
                ]
            }
        }

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