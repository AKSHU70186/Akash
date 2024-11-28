import aiohttp
import random
from typing import List
import asyncio

class ProxyRotator:
    def __init__(self):
        self.proxies: List[str] = []
        self.current_index = 0
        self.lock = asyncio.Lock()

    async def load_proxies(self):
        """Load proxies from various sources"""
        async with aiohttp.ClientSession() as session:
            # Load from proxy providers
            providers = [
                "https://proxy-provider1.com/api/proxies",
                "https://proxy-provider2.com/api/proxies"
            ]
            
            for provider in providers:
                try:
                    async with session.get(provider) as response:
                        if response.status == 200:
                            proxies = await response.json()
                            self.proxies.extend(proxies)
                except Exception as e:
                    print(f"Error loading proxies from {provider}: {e}")

    async def get_next_proxy(self) -> str:
        async with self.lock:
            if not self.proxies:
                await self.load_proxies()
            
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

    async def validate_proxy(self, proxy: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://httpbin.org/ip',
                    proxy=proxy,
                    timeout=5
                ) as response:
                    return response.status == 200
        except:
            return False 