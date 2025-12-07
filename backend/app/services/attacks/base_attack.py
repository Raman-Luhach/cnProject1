"""Base attack class for all attack implementations"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.attack import AttackStatus

logger = logging.getLogger(__name__)


class BaseAttack(ABC):
    """Abstract base class for all attacks"""
    
    def __init__(self, target_ip: str, target_port: Optional[int] = None, **kwargs):
        self.attack_id = str(uuid.uuid4())
        self.target_ip = target_ip
        self.target_port = target_port
        self.status = AttackStatus.IDLE
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.packets_sent = 0
        self.error_message: Optional[str] = None
        self.process = None
        self.task = None
        self.parameters = kwargs
    
    @abstractmethod
    async def _execute_attack(self):
        """Execute the attack (must be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def get_attack_type(self) -> str:
        """Get attack type name"""
        pass
    
    def get_default_port(self) -> int:
        """Get default port for this attack type"""
        return 80
    
    async def start(self):
        """Start the attack"""
        if self.status == AttackStatus.RUNNING:
            logger.warning(f"{self.get_attack_type()}: Attack already running")
            return
        
        try:
            self.status = AttackStatus.STARTING
            self.start_time = datetime.now()
            self.packets_sent = 0
            self.error_message = None
            
            logger.info(f"{self.get_attack_type()}: Starting attack on {self.target_ip}:{self.target_port or self.get_default_port()}")
            
            # Start attack in background task
            self.task = asyncio.create_task(self._run_attack())
            
            self.status = AttackStatus.RUNNING
            logger.info(f"{self.get_attack_type()}: Attack started (ID: {self.attack_id})")
            
        except Exception as e:
            self.status = AttackStatus.FAILED
            self.error_message = str(e)
            logger.error(f"{self.get_attack_type()}: Failed to start - {e}")
    
    async def _run_attack(self):
        """Run attack execution"""
        try:
            await self._execute_attack()
            if self.status == AttackStatus.RUNNING:
                self.status = AttackStatus.STOPPED
                self.end_time = datetime.now()
        except asyncio.CancelledError:
            logger.info(f"{self.get_attack_type()}: Attack cancelled")
            self.status = AttackStatus.STOPPED
            self.end_time = datetime.now()
        except Exception as e:
            self.status = AttackStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            logger.error(f"{self.get_attack_type()}: Attack failed - {e}")
    
    async def stop(self):
        """Stop the attack"""
        if self.status != AttackStatus.RUNNING:
            logger.warning(f"{self.get_attack_type()}: Attack not running")
            return
        
        try:
            self.status = AttackStatus.STOPPING
            logger.info(f"{self.get_attack_type()}: Stopping attack...")
            
            # Cancel the task
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            
            # Kill process if exists
            if self.process:
                try:
                    self.process.terminate()
                    await asyncio.sleep(1)
                    if self.process.poll() is None:
                        self.process.kill()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
            
            self.status = AttackStatus.STOPPED
            self.end_time = datetime.now()
            logger.info(f"{self.get_attack_type()}: Attack stopped")
            
        except Exception as e:
            self.status = AttackStatus.FAILED
            self.error_message = str(e)
            logger.error(f"{self.get_attack_type()}: Error stopping - {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get attack status"""
        return {
            'attack_id': self.attack_id,
            'attack_type': self.get_attack_type(),
            'status': self.status.value,
            'target_ip': self.target_ip,
            'target_port': self.target_port or self.get_default_port(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'packets_sent': self.packets_sent,
            'error_message': self.error_message
        }
    
    def is_running(self) -> bool:
        """Check if attack is running"""
        return self.status == AttackStatus.RUNNING

