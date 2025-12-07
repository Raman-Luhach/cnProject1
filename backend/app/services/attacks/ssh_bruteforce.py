"""SSH Brute Force attack implementation"""

import asyncio
import logging
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class SSHBruteForce(BaseAttack):
    """SSH brute force attack"""
    
    def get_attack_type(self) -> str:
        return "SSH-Bruteforce"
    
    def get_default_port(self) -> int:
        return 22
    
    async def _try_login(self, username, password):
        """Attempt SSH login"""
        port = self.target_port or self.get_default_port()
        
        # Simulated SSH connection attempt
        # In production, would use paramiko or asyncssh
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target_ip, port),
                timeout=5
            )
            
            # Read banner
            await asyncio.wait_for(reader.read(1024), timeout=2)
            
            self.packets_sent += 1
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Login attempt failed: {username}:{password} - {e}")
    
    async def _execute_attack(self):
        """Execute SSH brute force"""
        duration = self.parameters.get('duration', 300)
        
        # Common usernames and passwords
        usernames = ['root', 'admin', 'user', 'test', 'ubuntu', 'guest']
        passwords = ['password', '123456', 'admin', 'root', '12345678', 'test']
        
        logger.info(f"SSH-BruteForce: Starting attack on {self.target_ip}:22")
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            tasks = []
            for username in usernames:
                for password in passwords:
                    task = self._try_login(username, password)
                    tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            if self.packets_sent % 100 == 0:
                logger.info(f"SSH-BruteForce: {self.packets_sent} attempts")
            
            await asyncio.sleep(1)
        
        logger.info(f"SSH-BruteForce: Attack complete. Total attempts: {self.packets_sent}")

