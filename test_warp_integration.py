#!/usr/bin/env python3
"""
Test Warp Terminal integration
"""

import sys
import os
import yaml

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))

from notification_manager import NotificationManager

def test_warp_integration():
    """Test Warp Terminal integration"""
    print("Testing Warp Terminal integration...")
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create notification manager
    notification_manager = NotificationManager(config)
    
    # Create a test issue
    test_issue = {
        'type': 'system_error',
        'severity': 'warning',
        'title': 'Test System Error',
        'message': 'Testing Warp integration',
        'data': {
            'error_pattern': 'test_error',
            'error_message': 'This is a test error message for Warp integration testing'
        }
    }
    
    print("Launching Warp Terminal with test investigation prompt...")
    
    # Test the Warp launch functionality directly
    notification_manager._launch_warp_investigation(test_issue)
    
    print("Test completed. Check if Warp Terminal launched with the investigation prompt.")

if __name__ == '__main__':
    test_warp_integration()