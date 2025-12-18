#!/usr/bin/env python3
"""
MintWatcher - Linux Mint System Monitor
Monitors system performance and security with desktop notifications
"""

import argparse
import sys
import os
import yaml
import signal
import time
import threading
from pathlib import Path

# Add the monitors directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))

from system_monitor import SystemMonitor
from notification_manager import NotificationManager

class MintWatcher:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()
        self.monitor = SystemMonitor(self.config)
        self.notification_manager = NotificationManager(self.config)
        self.running = False
        self.monitor_thread = None
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {self.config_file} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
            
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
            
    def start_monitoring(self):
        """Start the monitoring daemon"""
        if self.is_running():
            print("MintWatcher is already running")
            return
            
        print("Starting MintWatcher monitoring...")
        self.running = True
        
        # Write PID file
        pid_file = self.config['daemon']['pid_file']
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Start monitoring loop
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
            
    def stop_monitoring(self):
        """Stop the monitoring daemon"""
        print("Stopping MintWatcher...")
        self.running = False
        
        # Remove PID file
        pid_file = self.config['daemon']['pid_file']
        if os.path.exists(pid_file):
            os.remove(pid_file)
            
    def stop_all_instances(self):
        """Stop all running MintWatcher processes"""
        import subprocess
        import signal
        
        print("Searching for running MintWatcher processes...")
        
        stopped_count = 0
        current_pid = os.getpid()
        
        # Method 1: Check PID file
        pid_file = self.config['daemon']['pid_file']
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if pid != current_pid:
                    print(f"Found MintWatcher process (PID: {pid}) from PID file")
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"Sent SIGTERM to process {pid}")
                        stopped_count += 1
                        
                        # Wait briefly and check if it's still running
                        import time
                        time.sleep(1)
                        try:
                            os.kill(pid, 0)  # Check if process exists
                            print(f"Process {pid} still running, sending SIGKILL...")
                            os.kill(pid, signal.SIGKILL)
                        except OSError:
                            print(f"Process {pid} terminated successfully")
                            
                    except OSError as e:
                        print(f"Could not terminate process {pid}: {e}")
                        
                # Remove stale PID file
                os.remove(pid_file)
                print(f"Removed PID file: {pid_file}")
                
            except (ValueError, OSError) as e:
                print(f"Error reading PID file: {e}")
                
        # Method 2: Search for mintwatcher processes using ps
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'mintwatcher.py' in line and 'python' in line:
                    # Parse the PID from ps output
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            
                            # Don't kill ourselves
                            if pid == current_pid:
                                continue
                                
                            print(f"Found MintWatcher process (PID: {pid})")
                            print(f"  Command: {' '.join(parts[10:15])}...")  # Show command
                            
                            try:
                                os.kill(pid, signal.SIGTERM)
                                print(f"Sent SIGTERM to process {pid}")
                                stopped_count += 1
                            except OSError as e:
                                print(f"Could not terminate process {pid}: {e}")
                                
                        except (ValueError, IndexError):
                            continue
                            
        except subprocess.CalledProcessError as e:
            print(f"Error searching for processes: {e}")
            
        if stopped_count > 0:
            print(f"\nStopped {stopped_count} MintWatcher process(es)")
        else:
            print("No running MintWatcher processes found")
            
    def is_running(self):
        """Check if MintWatcher daemon is running"""
        pid_file = self.config['daemon']['pid_file']
        if not os.path.exists(pid_file):
            return False
            
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # Process doesn't exist, remove stale PID file
            os.remove(pid_file)
            return False
            
    def get_status(self):
        """Get current monitoring status"""
        if self.is_running():
            print("Status: MintWatcher is running")
            # Get current system metrics
            metrics = self.monitor.get_current_metrics()
            print(f"CPU: {metrics['cpu_percent']:.1f}%")
            print(f"Memory: {metrics['memory_percent']:.1f}%")
            print(f"Disk: {metrics['disk_percent']:.1f}%")
        else:
            print("Status: MintWatcher is not running")
            
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Run system checks
                issues = self.monitor.check_system()
                
                # Send notifications for any issues found
                for issue in issues:
                    self.notification_manager.send_notification(issue)
                    
                # Wait for next check
                time.sleep(self.config['monitoring']['check_interval'])
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retrying
                
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.stop_monitoring()
        
def main():
    parser = argparse.ArgumentParser(
        description='MintWatcher - Linux Mint System Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='MintWatcher 1.0.0')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--status', action='store_true', help='Show current monitoring status')
    parser.add_argument('--enable', action='store_true', help='Enable monitoring daemon')
    parser.add_argument('--disable', action='store_true', help='Disable monitoring daemon')
    parser.add_argument('--start', action='store_true', help='Start monitoring (foreground)')
    parser.add_argument('--stop', action='store_true', help='Stop all running MintWatcher processes')
    
    args = parser.parse_args()
    
    # Change to script directory for relative config paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    watcher = MintWatcher(args.config)
    
    if args.status:
        watcher.get_status()
    elif args.stop:
        watcher.stop_all_instances()
    elif args.enable:
        # TODO: Create systemd service
        print("Creating systemd service for MintWatcher...")
        print("Run 'systemctl --user enable mintwatcher' to enable auto-start")
    elif args.disable:
        # TODO: Disable systemd service
        print("Disabling MintWatcher service...")
        print("Run 'systemctl --user disable mintwatcher' to disable auto-start")
    elif args.start:
        watcher.start_monitoring()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()