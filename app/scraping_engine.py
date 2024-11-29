from bs4 import BeautifulSoup
import aiohttp
import logging
from typing import Optional, Dict, List
import re
from urllib.parse import urlparse

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def get_website_type(self, url: str) -> Optional[str]:
        """Determine website type from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'news' in domain or 'article' in domain:
            return 'news'
        elif 'edu' in domain:
            return 'education'
        elif any(x in domain for x in ['career', 'job']):
            return 'career'
        return None

    async def fetch_html(self, url: str) -> str:
        """Fetch HTML content from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                raise Exception(f"Failed to fetch URL: {response.status}")

    async def scrape_website(self, url: str, website_type: str) -> List[Dict]:
        """Main scraping function"""
        try:
            html = await self.fetch_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            if website_type == 'news':
                return await self._scrape_news(soup, url)
            elif website_type == 'education':
                return await self._scrape_education(soup, url)
            elif website_type == 'career':
                return await self._scrape_career(soup, url)
            else:
                return await self._scrape_generic(soup, url)

        except Exception as e:
            logging.error(f"Scraping error: {str(e)}")
            raise

    async def _scrape_news(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Scrape news websites"""
        articles = []
        
        # Common article selectors
        article_selectors = [
            'article', '.article', '.post', '.news-item',
            'div[class*="article"]', 'div[class*="post"]'
        ]

        # Try to find articles
        for selector in article_selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    article = {}
                    
                    # Try to get title
                    title_elem = (item.find(['h1', 'h2', 'h3']) or 
                                item.find(class_=re.compile(r'title|heading')))
                    if title_elem:
                        article['title'] = title_elem.get_text(strip=True)
                    
                    # Try to get link
                    link_elem = title_elem.find('a') if title_elem else None
                    if link_elem and link_elem.get('href'):
                        article['link'] = link_elem['href']
                        if not article['link'].startswith('http'):
                            article['link'] = f"{url.rstrip('/')}/{article['link'].lstrip('/')}"
                    
                    # Try to get description
                    desc_elem = (item.find(['p', 'div'], class_=re.compile(r'desc|summary|content')) or 
                               item.find('p'))
                    if desc_elem:
                        article['description'] = desc_elem.get_text(strip=True)
                    
                    # Only add if we have at least title
                    if article.get('title'):
                        articles.append(article)
                
                if articles:
                    break

        return articles

    async def _scrape_education(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Scrape education websites"""
        # Similar to _scrape_news but with education-specific selectors
        return await self._scrape_news(soup, url)

    async def _scrape_career(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Scrape career websites"""
        # Similar to _scrape_news but with career-specific selectors
        return await self._scrape_news(soup, url)

    async def _scrape_generic(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Scrape any website for content"""
        return await self._scrape_news(soup, url)

scraping_engine = ScrapingEngine() 