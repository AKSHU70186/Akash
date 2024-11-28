import asyncio
import aiohttp
from typing import List, Dict

async def test_scraper(urls: List[Dict[str, str]]):
    async with aiohttp.ClientSession() as session:
        for url_info in urls:
            print(f"\nTesting {url_info['type']} scraper with URL: {url_info['url']}")
            
            try:
                async with session.post(
                    "http://localhost:8000/test-scrape",
                    data={
                        "url": url_info['url'],
                        "scraper_type": url_info['type']
                    }
                ) as response:
                    result = await response.json()
                    print("Status:", result['status'])
                    if result['status'] == 'success':
                        print("Data sample:", str(result['data'])[:200] + "...")
                    else:
                        print("Error:", result['message'])
            except Exception as e:
                print("Error:", str(e))

# Example URLs to test
test_urls = [
    {
        "type": "google_maps",
        "url": "https://www.google.com/maps/place/Starbucks"
    },
    {
        "type": "e_commerce",
        "url": "https://www.amazon.com/dp/B08N5KWB9H"
    },
    {
        "type": "news",
        "url": "https://www.bbc.com/news"
    },
    {
        "type": "social_media",
        "url": "https://twitter.com/elonmusk"
    },
    {
        "type": "job_board",
        "url": "https://www.indeed.com/jobs?q=python+developer"
    }
]

if __name__ == "__main__":
    asyncio.run(test_scraper(test_urls)) 