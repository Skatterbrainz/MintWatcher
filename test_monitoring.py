#!/usr/bin/env python3
"""
Test script for MintWatcher - validates basic monitoring functionality
"""

import sys
import os
import yaml

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))

from system_monitor import SystemMonitor

def test_basic_monitoring():
    """Test basic system monitoring functionality"""
    print("Testing MintWatcher monitoring capabilities...")
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create monitor
    monitor = SystemMonitor(config)
    
    # Test metrics collection
    print("\n1. Testing metrics collection:")
    metrics = monitor.get_current_metrics()
    print(f"   CPU: {metrics['cpu_percent']:.1f}%")
    print(f"   Memory: {metrics['memory_percent']:.1f}%")
    print(f"   Disk: {metrics['disk_percent']:.1f}%")
    print(f"   Memory used: {metrics['memory_used_mb']} MB")
    print(f"   Disk free: {metrics['disk_free_gb']} GB")
    
    # Test system checks
    print("\n2. Testing system checks:")
    issues = monitor.check_system()
    print(f"   Found {len(issues)} current issues:")
    
    for issue in issues:
        print(f"   - {issue['severity'].upper()}: {issue['title']}")
        print(f"     {issue['message']}")
    
    if not issues:
        print("   No issues detected (system is healthy)")
    
    print("\n3. Testing configuration:")
    print(f"   CPU threshold: {config['monitoring']['cpu_threshold']}%")
    print(f"   Memory threshold: {config['monitoring']['memory_threshold']}%")
    print(f"   Disk threshold: {config['monitoring']['disk_threshold']}%")
    print(f"   Check interval: {config['monitoring']['check_interval']}s")
    
    print("\nBasic monitoring test completed successfully!")
    return True

if __name__ == '__main__':
    try:
        test_basic_monitoring()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)