#!/usr/bin/env python3
"""
Test the Show button functionality
"""

import sys
import os
import yaml

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))

from notification_manager import NotificationManager

def test_show_functionality():
    """Test Show button functionality"""
    print("Testing Show button functionality...")
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create notification manager
    notification_manager = NotificationManager(config)
    
    # Create a test system error issue
    test_issue = {
        'type': 'system_error',
        'severity': 'warning',
        'title': 'System Log Error Detected',
        'message': 'Found system errors in logs',
        'data': {
            'error_pattern': 'error',
            'error_message': 'Test error message from journalctl',
            'error_count': 3
        }
    }
    
    print("Launching terminal to show issue details...")
    
    # Test the show functionality directly
    notification_manager._show_issue_details(test_issue)
    
    print("Test completed. Check if terminal opened with issue details and recent logs.")

if __name__ == '__main__':
    test_show_functionality()