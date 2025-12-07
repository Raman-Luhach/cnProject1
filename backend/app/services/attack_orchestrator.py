"""Attack Orchestrator - manages attack execution"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from app.models.attack import AttackType, AttackStatus
from app.services.attacks import *

logger = logging.getLogger(__name__)


class AttackOrchestrator:
    """Coordinates and manages attack execution"""
    
    def __init__(self):
        self.active_attacks: Dict[str, BaseAttack] = {}
        self.attack_history: List[Dict] = []
        
        # Attack type to class mapping
        self.attack_classes = {
            AttackType.DDOS_HOIC: DDosHOIC,
            AttackType.DDOS_LOIC_UDP: DDosLOICUDP,
            AttackType.DDOS_LOIC_HTTP: DDosLOICHTTP,
            AttackType.DOS_GOLDENEYE: DoSGoldenEye,
            AttackType.DOS_HULK: DoSHulk,
            AttackType.DOS_SLOWHTTPTEST: DoSSlowHTTPTest,
            AttackType.DOS_SLOWLORIS: DoSSlowloris,
            AttackType.BRUTE_FORCE_WEB: BruteForceWeb,
            AttackType.BRUTE_FORCE_XSS: BruteForceXSS,
            AttackType.FTP_BRUTEFORCE: FTPBruteForce,
            AttackType.SSH_BRUTEFORCE: SSHBruteForce,
            AttackType.SQL_INJECTION: SQLInjection
        }
    
    async def start_attack(
        self,
        attack_type: AttackType,
        target_ip: str,
        target_port: Optional[int] = None,
        duration: Optional[int] = None,
        **kwargs
    ) -> Optional[BaseAttack]:
        """Start an attack"""
        
        # Check if attack type is supported
        attack_class = self.attack_classes.get(attack_type)
        if not attack_class:
            logger.error(f"Unsupported attack type: {attack_type}")
            return None
        
        try:
            # Create attack instance
            attack = attack_class(
                target_ip=target_ip,
                target_port=target_port,
                duration=duration,
                **kwargs
            )
            
            # Start attack
            await attack.start()
            
            # Store active attack
            self.active_attacks[attack.attack_id] = attack
            
            logger.info(f"Started attack: {attack_type.value} (ID: {attack.attack_id})")
            
            return attack
            
        except Exception as e:
            logger.error(f"Failed to start attack {attack_type.value}: {e}")
            return None
    
    async def stop_attack(self, attack_id: str) -> bool:
        """Stop a specific attack"""
        attack = self.active_attacks.get(attack_id)
        
        if not attack:
            logger.warning(f"Attack {attack_id} not found")
            return False
        
        try:
            await attack.stop()
            
            # Move to history
            self.attack_history.append(attack.get_status())
            del self.active_attacks[attack_id]
            
            logger.info(f"Stopped attack: {attack_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping attack {attack_id}: {e}")
            return False
    
    async def stop_all_attacks(self) -> int:
        """Stop all active attacks"""
        count = 0
        attack_ids = list(self.active_attacks.keys())
        
        for attack_id in attack_ids:
            if await self.stop_attack(attack_id):
                count += 1
        
        logger.info(f"Stopped {count} attacks")
        return count
    
    def get_attack_status(self, attack_id: str) -> Optional[Dict]:
        """Get status of specific attack"""
        attack = self.active_attacks.get(attack_id)
        return attack.get_status() if attack else None
    
    def get_active_attacks(self) -> List[Dict]:
        """Get all active attacks"""
        return [attack.get_status() for attack in self.active_attacks.values()]
    
    def get_attack_history(self, limit: int = 100) -> List[Dict]:
        """Get attack history"""
        return self.attack_history[-limit:]
    
    def is_attack_running(self, attack_id: str) -> bool:
        """Check if attack is running"""
        attack = self.active_attacks.get(attack_id)
        return attack.is_running() if attack else False
    
    def get_available_attacks(self) -> List[Dict]:
        """Get list of available attack types"""
        return [
            {
                'name': attack_type.value,
                'display_name': attack_type.value,
                'description': f'{attack_type.value} attack',
                'default_port': attack_class(target_ip='0.0.0.0').get_default_port()
            }
            for attack_type, attack_class in self.attack_classes.items()
        ]


# Global orchestrator instance
_orchestrator = None


def get_attack_orchestrator() -> AttackOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AttackOrchestrator()
    return _orchestrator
