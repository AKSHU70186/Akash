from typing import Dict, Any
from bs4 import BeautifulSoup
import json

class ScrapingTemplate:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def extract_data(self, html: str) -> Dict[str, Any]:
        raise NotImplementedError

class EcommerceScraper(ScrapingTemplate):
    async def extract_data(self, html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'product_name': soup.select_one(self.config['selectors']['name']).text,
            'price': soup.select_one(self.config['selectors']['price']).text,
            'description': soup.select_one(self.config['selectors']['description']).text,
            'images': [img['src'] for img in soup.select(self.config['selectors']['images'])],
            'reviews': [
                {
                    'rating': review.select_one('.rating').text,
                    'comment': review.select_one('.comment').text,
                    'author': review.select_one('.author').text
                }
                for review in soup.select(self.config['selectors']['reviews'])
            ]
        }
        return data

class SocialMediaScraper(ScrapingTemplate):
    async def extract_data(self, html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'posts': [
                {
                    'content': post.select_one('.content').text,
                    'likes': post.select_one('.likes').text,
                    'comments': post.select_one('.comments').text,
                    'timestamp': post.select_one('.timestamp').text
                }
                for post in soup.select(self.config['selectors']['posts'])
            ]
        }
        return data

class JobBoardScraper(ScrapingTemplate):
    async def extract_data(self, html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'jobs': [
                {
                    'title': job.select_one('.title').text,
                    'company': job.select_one('.company').text,
                    'location': job.select_one('.location').text,
                    'salary': job.select_one('.salary').text,
                    'description': job.select_one('.description').text
                }
                for job in soup.select(self.config['selectors']['jobs'])
            ]
        }
        return data 