#!/usr/bin/env python3
"""
System Monitor - Core monitoring functionality for MintWatcher
"""

import psutil
import os
import subprocess
import re
import time
from collections import defaultdict
from datetime import datetime

class SystemMonitor:
    def __init__(self, config):
        self.config = config
        self.last_check_time = time.time()
        self.process_history = defaultdict(list)
        
    def get_current_metrics(self):
        """Get current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'memory_used_mb': memory.used // 1024 // 1024,
            'disk_free_gb': disk.free // 1024 // 1024 // 1024
        }
        
    def check_system(self):
        """Run all system checks and return list of issues"""
        issues = []
        current_time = time.time()
        
        # CPU and Memory checks
        issues.extend(self._check_cpu_usage())
        issues.extend(self._check_memory_usage())
        issues.extend(self._check_disk_usage())
        issues.extend(self._check_processes())
        
        # System log checks (if enabled)
        if self.config['monitoring']['log_monitoring']:
            issues.extend(self._check_system_logs())
            
        self.last_check_time = current_time
        return issues
        
    def _check_cpu_usage(self):
        """Check for high CPU usage"""
        issues = []
        cpu_percent = psutil.cpu_percent(interval=1)
        threshold = self.config['monitoring']['cpu_threshold']
        
        if cpu_percent > threshold:
            # Find process causing high CPU
            processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                             key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
            
            top_process = processes[0] if processes else None
            if top_process and top_process.info['name'] not in self.config['exclusions']['cpu_spikes']:
                issues.append({
                    'type': 'high_cpu',
                    'severity': 'warning',
                    'title': f'High CPU Usage ({cpu_percent:.1f}%)',
                    'message': f'System CPU usage is {cpu_percent:.1f}%, mainly caused by {top_process.info["name"]}',
                    'data': {
                        'cpu_percent': cpu_percent,
                        'process_name': top_process.info['name'],
                        'process_pid': top_process.info['pid']
                    }
                })
                
        return issues
        
    def _check_memory_usage(self):
        """Check for high memory usage"""
        issues = []
        memory = psutil.virtual_memory()
        threshold = self.config['monitoring']['memory_threshold']
        
        if memory.percent > threshold:
            # Find top memory consuming process
            processes = sorted(psutil.process_iter(['pid', 'name', 'memory_info']), 
                             key=lambda p: p.info['memory_info'].rss if p.info['memory_info'] else 0, 
                             reverse=True)
            
            top_process = processes[0] if processes else None
            if top_process and top_process.info['name'] not in self.config['exclusions']['processes']:
                memory_mb = top_process.info['memory_info'].rss // 1024 // 1024
                issues.append({
                    'type': 'high_memory',
                    'severity': 'warning',
                    'title': f'High Memory Usage ({memory.percent:.1f}%)',
                    'message': f'System memory usage is {memory.percent:.1f}%, top process: {top_process.info["name"]} ({memory_mb}MB)',
                    'data': {
                        'memory_percent': memory.percent,
                        'process_name': top_process.info['name'],
                        'process_pid': top_process.info['pid'],
                        'memory_mb': memory_mb
                    }
                })
                
        return issues
        
    def _check_disk_usage(self):
        """Check for low disk space"""
        issues = []
        
        # Check all mounted filesystems
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                threshold = self.config['monitoring']['disk_threshold']
                
                if usage.percent > threshold:
                    issues.append({
                        'type': 'disk_space',
                        'severity': 'critical' if usage.percent > 95 else 'warning',
                        'title': f'Low Disk Space ({usage.percent:.1f}%)',
                        'message': f'Disk {partition.mountpoint} is {usage.percent:.1f}% full',
                        'data': {
                            'mount_point': partition.mountpoint,
                            'usage_percent': usage.percent,
                            'free_gb': usage.free // 1024 // 1024 // 1024
                        }
                    })
            except PermissionError:
                # Skip partitions we can't access
                continue
                
        return issues
        
    def _check_processes(self):
        """Check for suspicious or problematic processes"""
        issues = []
        
        if not self.config['monitoring']['suspicious_process_check']:
            return issues
            
        # List of potentially suspicious process patterns
        suspicious_patterns = [
            r'.*miner.*',
            r'.*crypto.*',
            r'.*malware.*',
            r'.*trojan.*',
            r'.*backdoor.*'
        ]
        
        # Common legitimate processes to ignore
        known_safe = {
            'systemd', 'kthreadd', 'ksoftirqd', 'migration', 'rcu_', 'watchdog',
            'bash', 'zsh', 'fish', 'python', 'python3', 'node', 'firefox',
            'chrome', 'chromium', 'code', 'vim', 'nano', 'gedit'
        }
        
        for process in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                name = process.info['name']
                
                # Skip known safe processes
                if any(safe in name.lower() for safe in known_safe):
                    continue
                    
                # Skip processes in exclusion list
                if name in self.config['exclusions']['processes']:
                    continue
                    
                # Check for suspicious patterns
                for pattern in suspicious_patterns:
                    if re.match(pattern, name.lower()):
                        issues.append({
                            'type': 'suspicious_process',
                            'severity': 'critical',
                            'title': f'Suspicious Process Detected',
                            'message': f'Process {name} (PID: {process.info["pid"]}) may be suspicious',
                            'data': {
                                'process_name': name,
                                'pid': process.info['pid'],
                                'cmdline': ' '.join(process.info['cmdline']) if process.info['cmdline'] else '',
                                'create_time': process.info['create_time']
                            }
                        })
                        break
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return issues
        
    def _check_system_logs(self):
        """Check system logs for errors and warnings"""
        issues = []
        
        try:
            # Check recent system logs
            cmd = ['journalctl', '--since', '5 minutes ago', '--no-pager', '-q']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                log_content = result.stdout.lower()
                
                for pattern in self.config['monitoring']['log_patterns']:
                    if pattern in self.config['exclusions']['log_patterns']:
                        continue
                        
                    if pattern in log_content:
                        # Extract the actual error line
                        lines = result.stdout.split('\n')
                        error_lines = [line for line in lines if pattern in line.lower()]
                        
                        if error_lines:
                            issues.append({
                                'type': 'system_error',
                                'severity': 'warning',
                                'title': f'System Log Error',
                                'message': f'Found {len(error_lines)} log entries containing "{pattern}"',
                                'data': {
                                    'error_pattern': pattern,
                                    'error_message': error_lines[0][:200],  # Truncate long messages
                                    'error_count': len(error_lines)
                                }
                            })
                            break  # Only report first pattern match to avoid spam
                            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # journalctl might not be available or accessible
            pass
            
        return issues