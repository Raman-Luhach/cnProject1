"""VM Manager - Multipass integration"""

import subprocess
import logging
import asyncio
import json
from typing import Optional, Dict, List
from datetime import datetime
from app.config import VM_NAME, VM_IP, VM_CPUS, VM_MEMORY, VM_DISK, VM_SERVICES
from app.models.vm import VMInfo, VMState, VMServiceStatus

logger = logging.getLogger(__name__)


class VMManager:
    """Manages Multipass VMs for IDS testing"""
    
    def __init__(self, vm_name: str = VM_NAME):
        self.vm_name = vm_name
    
    async def create_vm(
        self,
        cpus: int = VM_CPUS,
        memory: str = VM_MEMORY,
        disk: str = VM_DISK,
        install_services: bool = True
    ) -> tuple[bool, Optional[VMInfo], List[str]]:
        """Create a new VM with Multipass"""
        setup_log = []
        
        try:
            # Check if VM already exists
            if await self.vm_exists():
                setup_log.append(f"VM {self.vm_name} already exists")
                logger.warning(f"VM {self.vm_name} already exists")
                vm_info = await self.get_vm_info()
                return False, vm_info, setup_log
            
            # Create VM
            setup_log.append(f"Creating VM: {self.vm_name}")
            logger.info(f"Creating VM: {self.vm_name}")
            
            cmd = [
                'multipass', 'launch',
                '--name', self.vm_name,
                '--cpus', str(cpus),
                '--memory', memory,
                '--disk', disk
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                setup_log.append(f"Error: {error_msg}")
                logger.error(f"Failed to create VM: {error_msg}")
                return False, None, setup_log
            
            setup_log.append("VM created successfully")
            logger.info("VM created successfully")
            
            # Wait for VM to be ready
            await asyncio.sleep(5)
            
            # Install services if requested
            if install_services:
                setup_log.append("Installing services...")
                success, service_logs = await self._install_services()
                setup_log.extend(service_logs)
                
                if not success:
                    setup_log.append("Warning: Some services failed to install")
            
            # Get VM info
            vm_info = await self.get_vm_info()
            setup_log.append(f"VM IP: {vm_info.ipv4 if vm_info else 'Unknown'}")
            
            return True, vm_info, setup_log
            
        except Exception as e:
            error_msg = f"Error creating VM: {e}"
            setup_log.append(error_msg)
            logger.error(error_msg)
            return False, None, setup_log
    
    async def _install_services(self) -> tuple[bool, List[str]]:
        """Install services on VM"""
        logs = []
        all_success = True
        
        try:
            # Update package list
            logs.append("Updating package list...")
            update_cmd = ['multipass', 'exec', self.vm_name, '--', 'sudo', 'apt-get', 'update']
            result = await asyncio.create_subprocess_exec(
                *update_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            if result.returncode == 0:
                logs.append("✓ Package list updated")
            else:
                logs.append("✗ Failed to update package list")
                all_success = False
            
            # Install each service
            for service_name, service_config in VM_SERVICES.items():
                logs.append(f"Installing {service_name}...")
                
                install_cmd = service_config['install_cmd'].split()
                cmd = ['multipass', 'exec', self.vm_name, '--', 'sudo'] + install_cmd
                
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    logs.append(f"✓ {service_name} installed")
                else:
                    logs.append(f"✗ {service_name} failed to install")
                    all_success = False
            
            return all_success, logs
            
        except Exception as e:
            logs.append(f"Error installing services: {e}")
            return False, logs
    
    async def start_vm(self) -> bool:
        """Start the VM"""
        try:
            logger.info(f"Starting VM: {self.vm_name}")
            
            cmd = ['multipass', 'start', self.vm_name]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"Failed to start VM: {stderr.decode()}")
                return False
            
            logger.info("VM started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting VM: {e}")
            return False
    
    async def stop_vm(self) -> bool:
        """Stop the VM"""
        try:
            logger.info(f"Stopping VM: {self.vm_name}")
            
            cmd = ['multipass', 'stop', self.vm_name]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"Failed to stop VM: {stderr.decode()}")
                return False
            
            logger.info("VM stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping VM: {e}")
            return False
    
    async def delete_vm(self) -> bool:
        """Delete the VM"""
        try:
            logger.info(f"Deleting VM: {self.vm_name}")
            
            # Stop first
            await self.stop_vm()
            
            # Delete
            cmd = ['multipass', 'delete', self.vm_name]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            # Purge
            cmd = ['multipass', 'purge']
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            logger.info("VM deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting VM: {e}")
            return False
    
    async def vm_exists(self) -> bool:
        """Check if VM exists"""
        try:
            cmd = ['multipass', 'list', '--format', 'json']
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                return False
            
            data = json.loads(stdout.decode())
            vms = data.get('list', [])
            
            for vm in vms:
                if vm.get('name') == self.vm_name:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking VM existence: {e}")
            return False
    
    async def get_vm_info(self) -> Optional[VMInfo]:
        """Get VM information"""
        try:
            cmd = ['multipass', 'info', self.vm_name, '--format', 'json']
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                return None
            
            data = json.loads(stdout.decode())
            info = data.get('info', {}).get(self.vm_name, {})
            
            if not info:
                return None
            
            # Parse state
            state_str = info.get('state', 'unknown').lower()
            state_mapping = {
                'running': VMState.RUNNING,
                'stopped': VMState.STOPPED,
                'starting': VMState.STARTING,
                'stopping': VMState.STOPPING,
                'deleted': VMState.DELETED
            }
            state = state_mapping.get(state_str, VMState.UNKNOWN)
            
            # Get IPs
            ipv4 = info.get('ipv4', [None])[0] if info.get('ipv4') else None
            ipv6 = info.get('ipv6', [None])[0] if info.get('ipv6') else None
            
            # Get resource info
            cpus = info.get('cpus', 0)
            
            # Convert memory from dict to string if needed
            memory_raw = info.get('memory', '0')
            if isinstance(memory_raw, dict):
                # Multipass returns memory as {'total': bytes, 'used': bytes}
                total_bytes = memory_raw.get('total', 0)
                # Convert to human-readable format
                if total_bytes >= 1024 * 1024 * 1024:
                    memory = f"{total_bytes / (1024 * 1024 * 1024):.1f}G"
                elif total_bytes >= 1024 * 1024:
                    memory = f"{total_bytes / (1024 * 1024):.1f}M"
                else:
                    memory = f"{total_bytes / 1024:.1f}K"
            else:
                memory = str(memory_raw) if memory_raw else '0'
            
            # Convert disk from dict to string if needed
            disk_raw = info.get('disk', '0')
            if isinstance(disk_raw, dict):
                # Multipass returns disk as {'total': bytes, 'used': bytes}
                total_bytes = disk_raw.get('total', 0)
                # Convert to human-readable format
                if total_bytes >= 1024 * 1024 * 1024:
                    disk = f"{total_bytes / (1024 * 1024 * 1024):.1f}G"
                elif total_bytes >= 1024 * 1024:
                    disk = f"{total_bytes / (1024 * 1024):.1f}M"
                else:
                    disk = f"{total_bytes / 1024:.1f}K"
            else:
                disk = str(disk_raw) if disk_raw else '0'
            
            vm_info = VMInfo(
                name=self.vm_name,
                state=state,
                ipv4=ipv4,
                ipv6=ipv6,
                cpus=cpus,
                memory=memory,
                disk=disk,
                services=[],
                created_at=None
            )
            
            return vm_info
            
        except Exception as e:
            logger.error(f"Error getting VM info: {e}")
            return None
    
    async def get_vm_ip(self) -> Optional[str]:
        """Get VM IP address"""
        info = await self.get_vm_info()
        if info and info.ipv4:
            return info.ipv4
        
        # Fallback to configured default IP if VM exists but info unavailable
        exists = await self.vm_exists()
        if exists:
            logger.info(f"VM {self.vm_name} exists but IP not available, using default: {VM_IP}")
            return VM_IP
        
        return None


# Global VM manager instance
_vm_manager = None


def get_vm_manager() -> VMManager:
    """Get or create global VM manager instance"""
    global _vm_manager
    if _vm_manager is None:
        _vm_manager = VMManager()
    return _vm_manager

