#!/usr/bin/env python3
"""
MintWatcher - Linux Mint System Monitor
One-shot system checker with issue reporting and diagnostics
"""

import argparse
import sys
import os
import yaml
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Add the monitors directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))

from system_monitor import SystemMonitor

class MintWatcher:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()
        self.monitor = SystemMonitor(self.config)
        self.cache_file = '/tmp/mintwatcher_last_check.json'
        
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
            
    def check_system(self):
        """Run system check and display numbered findings"""
        issues = self.monitor.check_system()
        
        if not issues:
            print("✓ No issues detected. System is healthy.")
            # Clear cache if no issues
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            return
        
        # Cache issues for diagnose command
        self._cache_issues(issues)
        
        # Display issues with numbers
        print(f"\n⚠ Found {len(issues)} issue(s):\n")
        
        for idx, issue in enumerate(issues, 1):
            severity_color = self._get_color_for_severity(issue['severity'])
            reset = "\033[0m"
            
            print(f"{severity_color}{idx}. [{issue['severity'].upper()}] {issue['title']}{reset}")
            print(f"   {issue['message']}")
            
            # Show key data points
            issue_data = issue.get('data', {})
            if issue_data:
                key_info = []
                if 'process_name' in issue_data:
                    key_info.append(f"Process: {issue_data['process_name']}")
                if 'cpu_percent' in issue_data:
                    key_info.append(f"CPU: {issue_data['cpu_percent']}%")
                if 'memory_mb' in issue_data:
                    key_info.append(f"Memory: {issue_data['memory_mb']}MB")
                if 'usage_percent' in issue_data:
                    key_info.append(f"Usage: {issue_data['usage_percent']}%")
                
                if key_info:
                    print(f"   {' | '.join(key_info)}")
            print()
        
        print(f"To diagnose an issue, run: {sys.argv[0]} --diagnose <number>")
        print()
    
    def diagnose_issue(self, issue_number):
        """Generate diagnostic script for a specific issue"""
        issues = self._load_cached_issues()
        
        if not issues:
            print("Error: No cached issues found. Run --check first.")
            sys.exit(1)
        
        if issue_number < 1 or issue_number > len(issues):
            print(f"Error: Issue number must be between 1 and {len(issues)}")
            sys.exit(1)
        
        issue = issues[issue_number - 1]
        
        # Create investigation script
        self._create_investigation_script(issue, issue_number)
    
    def _cache_issues(self, issues):
        """Cache issues to temp file for diagnose command"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'issues': issues
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def _load_cached_issues(self):
        """Load cached issues from temp file"""
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            return cache_data.get('issues', [])
        except (json.JSONDecodeError, IOError):
            return None
    
    def _create_investigation_script(self, issue, issue_number):
        """Create Warp investigation script for an issue"""
        import subprocess
        
        issue_type = issue['type']
        issue_data = issue.get('data', {})
        
        # Get investigation prompt template
        prompt_template = self.config['warp']['investigation_prompts'].get(issue_type)
        if not prompt_template:
            prompt_template = f"Investigate system issue: {issue['message']}"
        
        # Format prompt with issue data
        try:
            prompt = prompt_template.format(**issue_data)
        except KeyError:
            prompt = f"Investigate system issue: {issue['message']}"
        
        # Create investigation script
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"investigate_{issue_type}_{timestamp}.sh"
        filepath = os.path.expanduser(f"~/MintWatcher_Commands/{filename}")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create script with detailed comments
        warp_command = self.config['warp']['terminal_command']
        script_content = f"""#!/bin/bash
# MintWatcher Investigation Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Issue #{issue_number}: {issue['title']}
# Type: {issue_type}
# Severity: {issue['severity']}

echo "MintWatcher Investigation"
echo "========================="
echo "Issue #{issue_number}: {issue['title']}"
echo ""
echo "Launching Warp Terminal AI..."
echo ""

# Run Warp Terminal with investigation prompt
{warp_command} agent run --prompt '{prompt}'
"""
        
        with open(filepath, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(filepath, 0o755)
        
        print(f"\n✓ Investigation script created: {filepath}")
        print(f"\nTo investigate, run:\n  bash {filepath}\n")
        
        # Try to open with editor
        try:
            subprocess.Popen(
                ['xed', filepath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"Script opened in editor.\n")
        except:
            pass
    
    def _get_color_for_severity(self, severity):
        """Get ANSI color code for severity level"""
        colors = {
            'critical': '\033[91m',  # Red
            'warning': '\033[93m',   # Yellow
            'info': '\033[96m'       # Cyan
        }
        return colors.get(severity, '\033[0m')
        
def main():
    parser = argparse.ArgumentParser(
        description='MintWatcher - Linux Mint System Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='MintWatcher 2.0.0')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--check', action='store_true', help='Check system and list all issues')
    parser.add_argument('--diagnose', type=int, metavar='N', help='Create diagnostic script for issue number N')
    
    args = parser.parse_args()
    
    # Change to script directory for relative config paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    watcher = MintWatcher(args.config)
    
    if args.check:
        watcher.check_system()
    elif args.diagnose is not None:
        watcher.diagnose_issue(args.diagnose)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
