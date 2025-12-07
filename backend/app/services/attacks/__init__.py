"""Attack modules for testing IDS"""

from .base_attack import BaseAttack
from .ddos_hoic import DDosHOIC
from .ddos_loic_udp import DDosLOICUDP
from .ddos_loic_http import DDosLOICHTTP
from .dos_goldeneye import DoSGoldenEye
from .dos_hulk import DoSHulk
from .dos_slowhttptest import DoSSlowHTTPTest
from .dos_slowloris import DoSSlowloris
from .brute_force_web import BruteForceWeb
from .brute_force_xss import BruteForceXSS
from .ftp_bruteforce import FTPBruteForce
from .ssh_bruteforce import SSHBruteForce
from .sql_injection import SQLInjection

__all__ = [
    'BaseAttack',
    'DDosHOIC',
    'DDosLOICUDP',
    'DDosLOICHTTP',
    'DoSGoldenEye',
    'DoSHulk',
    'DoSSlowHTTPTest',
    'DoSSlowloris',
    'BruteForceWeb',
    'BruteForceXSS',
    'FTPBruteForce',
    'SSHBruteForce',
    'SQLInjection'
]

