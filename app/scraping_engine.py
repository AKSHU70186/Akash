from bs4 import BeautifulSoup
import aiohttp
import logging
from typing import Dict, List
import re
from urllib.parse import urljoin

class ScrapingEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        self.news_sites = {
            'indianexpress.com': {
                'article_wrapper': 'div.article-list article',
                'title': 'h2.title',
                'link': 'h2.title a',
                'description': 'p.preview',
                'date': 'div.date'
            },
            'careers360.com': {
                'article_wrapper': 'div.newsListBlock',
                'title': 'h3.headingText',
                'link': 'a',
                'description': 'p.content',
                'date': 'span.date'
            },
            'ndtv.com': {
                'article_wrapper': 'div.news_item',
                'title': 'h2.newsHdng',
                'link': 'a',
                'description': 'p.newsCont',
                'date': 'span.posted-on'
            }
        }

    async def fetch_html(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.text()
                    raise Exception(f"Failed to fetch URL: {response.status}")
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            raise Exception(f"Failed to fetch content: {str(e)}")

    def get_site_config(self, url: str) -> Dict:
        for domain, config in self.news_sites.items():
            if domain in url:
                return config
        return None

    async def scrape_website(self, url: str, website_type: str = None) -> List[Dict]:
        try:
            html = await self.fetch_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            # Get site-specific config
            site_config = self.get_site_config(url)
            
            if site_config:
                # Use site-specific selectors
                articles = self.extract_articles_with_config(soup, url, site_config)
            else:
                # Fallback to generic selectors
                articles = self.extract_articles_generic(soup, url)

            return articles

        except Exception as e:
            logging.error(f"Scraping error: {str(e)}")
            raise

    def extract_articles_with_config(self, soup: BeautifulSoup, base_url: str, config: Dict) -> List[Dict]:
        articles = []
        for article in soup.select(config['article_wrapper']):
            try:
                # Extract title
                title_elem = article.select_one(config['title'])
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Extract link
                link_elem = article.select_one(config['link'])
                link = link_elem.get('href') if link_elem else None
                if link and not link.startswith('http'):
                    link = urljoin(base_url, link)

                # Extract description
                desc_elem = article.select_one(config['description'])
                description = desc_elem.get_text(strip=True) if desc_elem else None

                # Extract date
                date_elem = article.select_one(config['date'])
                date = date_elem.get_text(strip=True) if date_elem else None

                articles.append({
                    'title': title,
                    'link': link,
                    'description': description,
                    'date': date,
                    'source': base_url
                })
            except Exception as e:
                logging.error(f"Error extracting article: {str(e)}")
                continue

        return articles

    def extract_articles_generic(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        articles = []
        # Generic article selectors
        article_selectors = [
            'article', 
            '.article', 
            '.news-item',
            '.post',
            'div[class*="article"]',
            'div[class*="news"]',
            '.story-box'
        ]

        for selector in article_selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    try:
                        # Find title
                        title_elem = (
                            item.find(['h1', 'h2', 'h3', 'h4']) or 
                            item.find(class_=re.compile(r'title|heading', re.I))
                        )
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        
                        # Find link
                        link_elem = title_elem.find('a') or item.find('a')
                        link = link_elem.get('href') if link_elem else None
                        if link and not link.startswith('http'):
                            link = urljoin(base_url, link)

                        # Find description
                        desc_elem = (
                            item.find(['p', 'div'], class_=re.compile(r'desc|summary|content', re.I)) or
                            item.find('p')
                        )
                        description = desc_elem.get_text(strip=True) if desc_elem else None

                        articles.append({
                            'title': title,
                            'link': link,
                            'description': description,
                            'source': base_url
                        })
                    except Exception as e:
                        logging.error(f"Error extracting article: {str(e)}")
                        continue

                if articles:
                    break

        return articles

scraping_engine = ScrapingEngine() 