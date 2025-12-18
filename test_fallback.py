#!/usr/bin/env python3
"""
Test both terminal launch and fallback functionality
"""

import sys
import os
import yaml

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))

from notification_manager import NotificationManager

def test_fallback_functionality():
    """Test fallback command file creation"""
    print("Testing fallback functionality...")
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create notification manager
    notification_manager = NotificationManager(config)
    
    # Create a test issue
    test_issue = {
        'type': 'high_cpu',
        'severity': 'warning',
        'title': 'High CPU Usage Detected',
        'message': 'Process consuming excessive CPU',
        'data': {
            'process_name': 'test_process',
            'cpu_percent': 95.5,
            'process_pid': 12345
        }
    }
    
    print("Testing fallback command file creation...")
    
    # Test creating command files directly
    notification_manager._create_command_file(test_issue, "investigate")
    notification_manager._create_command_file(test_issue, "show")
    
    print("\nFallback test completed. Check ~/MintWatcher_Commands/ for generated scripts.")
    
    # List the created files
    import glob
    commands_dir = os.path.expanduser("~/MintWatcher_Commands")
    if os.path.exists(commands_dir):
        files = glob.glob(os.path.join(commands_dir, "*.sh"))
        print(f"\nCreated command files:")
        for file in sorted(files)[-2:]:  # Show last 2 files
            print(f"  - {file}")
            print(f"    To run: bash {file}")

if __name__ == '__main__':
    test_fallback_functionality()