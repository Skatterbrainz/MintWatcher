#!/usr/bin/env python3
"""
Notification Manager - Handles desktop notifications with interactive buttons
"""

import gi
import subprocess
import yaml
import hashlib
import os
from datetime import datetime

gi.require_version('Notify', '0.7')
from gi.repository import Notify, GLib

class NotificationManager:
    def __init__(self, config):
        self.config = config
        self.config_file = 'config.yaml'  # Assume config file is in same directory
        
        # Initialize libnotify
        Notify.init("MintWatcher")
        
        # Keep track of active notifications to prevent spam
        self.active_notifications = {}
        
    def send_notification(self, issue):
        """Send notification and prompt for action in terminal"""
        if not self.config['notifications']['enabled']:
            return
            
        # Create unique ID for this issue type to prevent duplicates
        issue_id = self._generate_issue_id(issue)
        
        # Check if we already have an active notification for this issue
        if issue_id in self.active_notifications:
            return
            
        # Check if this issue is in the exclusions list
        if self._is_excluded(issue):
            return
            
        # Send desktop notification (simple, no buttons)
        try:
            notification = Notify.Notification.new(
                issue['title'],
                issue['message'],
                self._get_icon_for_severity(issue['severity'])
            )
            notification.set_timeout(5000)  # 5 seconds
            notification.show()
        except Exception as e:
            print(f"Failed to send notification: {e}")
            
        # Display in terminal with interactive prompt
        self._terminal_prompt(issue, issue_id)
            
    def _terminal_prompt(self, issue, issue_id):
        """Display issue in terminal and prompt for action"""
        import sys
        
        # Mark as active to prevent duplicates
        self.active_notifications[issue_id] = True
        
        # Display the issue with colors
        print("\n" + "="*60)
        severity_color = "\033[91m" if issue['severity'] == 'critical' else "\033[93m"
        reset_color = "\033[0m"
        print(f"{severity_color}⚠ {issue['title']}{reset_color}")
        print("="*60)
        print(f"Message: {issue['message']}")
        
        # Show relevant data
        issue_data = issue.get('data', {})
        if issue_data:
            print("\nDetails:")
            for key, value in issue_data.items():
                print(f"  {key}: {value}")
        
        print("\n" + "-"*60)
        print("Actions:")
        print("  [S]how    - View full details in text editor")
        print("  [D]iagnose - Create Warp investigation script")
        print("  [I]gnore  - Add to exclusions (won't alert again)")
        print("  [Enter]   - Skip for now")
        print("-"*60)
        
        try:
            # Non-blocking input with timeout
            response = input("Choose action (S/D/I/Enter): ").strip().lower()
            
            if response == 's':
                print("Creating detailed report...")
                self._show_issue_details(issue)
            elif response == 'd':
                print("Creating investigation script...")
                self._launch_warp_investigation(issue)
            elif response == 'i':
                print("Adding to exclusions...")
                self._add_to_exclusions(issue)
                print("Issue ignored. Won't alert again.")
            else:
                print("Skipped.")
                
        except (EOFError, KeyboardInterrupt):
            print("\nSkipped.")
        finally:
            # Remove from active notifications
            if issue_id in self.active_notifications:
                del self.active_notifications[issue_id]
        
        print("")
        
    def _generate_issue_id(self, issue):
        """Generate a unique ID for an issue type"""
        # Create ID based on issue type and key identifying information
        id_string = f"{issue['type']}_{issue.get('data', {}).get('process_name', '')}"
        return hashlib.md5(id_string.encode()).hexdigest()[:8]
        
    def _is_excluded(self, issue):
        """Check if this issue type is excluded from notifications"""
        issue_type = issue['type']
        issue_data = issue.get('data', {})
        
        # Check process exclusions
        if issue_type in ['high_cpu', 'high_memory', 'suspicious_process']:
            process_name = issue_data.get('process_name', '')
            if process_name in self.config['exclusions']['processes']:
                return True
                
        # Check CPU spike exclusions
        if issue_type == 'high_cpu':
            process_name = issue_data.get('process_name', '')
            if process_name in self.config['exclusions']['cpu_spikes']:
                return True
                
        # Check log pattern exclusions
        if issue_type == 'system_error':
            error_pattern = issue_data.get('error_pattern', '')
            if error_pattern in self.config['exclusions']['log_patterns']:
                return True
                
        return False
        
    def _get_icon_for_severity(self, severity):
        """Get appropriate icon for notification severity"""
        icons = {
            'critical': 'dialog-error',
            'warning': 'dialog-warning',
            'info': 'dialog-information'
        }
        return icons.get(severity, 'dialog-information')
        
            
    def _add_to_exclusions(self, issue):
        """Add issue to exclusions list in config"""
        issue_type = issue['type']
        issue_data = issue.get('data', {})
        
        modified = False
        
        # Add process to exclusions
        if issue_type in ['high_cpu', 'high_memory', 'suspicious_process']:
            process_name = issue_data.get('process_name')
            if process_name and process_name not in self.config['exclusions']['processes']:
                self.config['exclusions']['processes'].append(process_name)
                modified = True
                
        # Add CPU spike exclusion
        elif issue_type == 'high_cpu':
            process_name = issue_data.get('process_name')
            if process_name and process_name not in self.config['exclusions']['cpu_spikes']:
                self.config['exclusions']['cpu_spikes'].append(process_name)
                modified = True
                
        # Add log pattern exclusion
        elif issue_type == 'system_error':
            error_pattern = issue_data.get('error_pattern')
            if error_pattern and error_pattern not in self.config['exclusions']['log_patterns']:
                self.config['exclusions']['log_patterns'].append(error_pattern)
                modified = True
                
        # Save config if modified
        if modified:
            self._save_config()
            print(f"Added exclusion for {issue_type}")
            
    def _launch_warp_investigation(self, issue):
        """Create investigation script and open for review/execution"""
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
            # Fallback if formatting fails
            prompt = f"Investigate system issue: {issue['message']}"
            
        # Launch Warp Terminal
        warp_command = self.config['warp']['terminal_command']
        
        try:
            # Create investigation script
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"investigate_{issue_type}_{timestamp}.sh"
            filepath = os.path.expanduser(f"~/MintWatcher_Commands/{filename}")
            
            # Create directory if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create script with detailed comments
            script_content = f"""#!/bin/bash
# MintWatcher Investigation Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Issue: {issue['title']}
# Type: {issue_type}
# Severity: {issue['severity']}

# This script will launch Warp Terminal AI to investigate the issue.
# Simply run this script to start the investigation:
#   bash {filename}
# Or make it executable and run:
#   chmod +x {filename}
#   ./{filename}

echo "MintWatcher Investigation"
echo "========================="
echo "Issue: {issue['title']}"
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
            print(f"  Opening in editor...")
            
            # Try to open with default editor
            try:
                subprocess.Popen(
                    ['xed', filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"  Opened with xed")
            except:
                try:
                    subprocess.Popen(
                        ['xdg-open', filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"  Opened with xdg-open")
                except:
                    print(f"  Could not open automatically")
            
            print(f"\n  To investigate, run: bash {filepath}")
            return True
            
        except Exception as e:
            print(f"Failed to create investigation script: {e}")
            print(f"Investigation prompt: {prompt}")
            return False
            
    def _show_issue_details(self, issue):
        """Show issue details by creating and opening a text file"""
        import tempfile
        import subprocess
        
        issue_type = issue['type']
        issue_data = issue.get('data', {})
        
        try:
            # Create a text file with issue details
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            details = f"MintWatcher Issue Report\n"
            details += f"Generated: {timestamp}\n"
            details += f"{'='*60}\n\n"
            details += f"Issue Type: {issue_type}\n"
            details += f"Severity: {issue['severity'].upper()}\n"
            details += f"Title: {issue['title']}\n"
            details += f"Message: {issue['message']}\n\n"
            
            if issue_data:
                details += f"Additional Details:\n"
                details += f"{'-'*60}\n"
                for key, value in issue_data.items():
                    details += f"  {key}: {value}\n"
                details += "\n"
            
            # For log errors, add recent logs
            if issue_type == 'system_error':
                details += f"\nRecent System Logs:\n"
                details += f"{'-'*60}\n"
                try:
                    result = subprocess.run(
                        ['journalctl', '--since', '10 minutes ago', '--no-pager', '-q'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        log_lines = result.stdout.strip().split('\n')[-20:]  # Last 20 lines
                        details += '\n'.join(log_lines)
                    else:
                        details += "(Unable to fetch system logs)\n"
                except Exception as e:
                    details += f"(Error fetching logs: {e})\n"
            
            # Create file in home directory for easy access
            filename = f"mintwatcher_issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.expanduser(f"~/MintWatcher_Reports/{filename}")
            
            # Create directory if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write the file
            with open(filepath, 'w') as f:
                f.write(details)
            
            print(f"\n✓ Issue details saved to: {filepath}")
            print(f"  Opening in editor...")
            
            # Try to open with default editor
            try:
                subprocess.Popen(
                    ['xed', filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"  Opened with xed")
            except:
                try:
                    subprocess.Popen(
                        ['xdg-open', filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"  Opened with xdg-open")
                except:
                    print(f"  Could not open automatically. Open manually:")
                    print(f"  xed {filepath}")
            
            return True
            
        except Exception as e:
            print(f"Failed to show issue details: {e}")
            return False
            
    def _save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            
    def _create_command_file(self, issue, action_type):
        """Create a command file as fallback when terminal launch fails"""
        import os
        
        try:
            # Create commands directory if it doesn't exist
            commands_dir = os.path.expanduser("~/MintWatcher_Commands")
            os.makedirs(commands_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{action_type}_{issue['type']}_{timestamp}.sh"
            filepath = os.path.join(commands_dir, filename)
            
            if action_type == "investigate":
                # Create Warp investigation command
                issue_data = issue.get('data', {})
                prompt_template = self.config['warp']['investigation_prompts'].get(issue['type'])
                if prompt_template:
                    try:
                        prompt = prompt_template.format(**issue_data)
                    except KeyError:
                        prompt = f"Investigate system issue: {issue['message']}"
                else:
                    prompt = f"Investigate system issue: {issue['message']}"
                    
                command = f"warp-terminal agent run --prompt '{prompt}'"
                
            elif action_type == "show":
                # Create show details command
                issue_data = issue.get('data', {})
                details = f"echo 'MintWatcher Issue Details:'"
                details += f" && echo 'Type: {issue['type']}'"
                details += f" && echo 'Severity: {issue['severity']}'"
                details += f" && echo 'Title: {issue['title']}'"
                details += f" && echo 'Message: {issue['message']}'"
                
                if issue_data:
                    details += " && echo 'Additional Data:'"
                    for key, value in issue_data.items():
                        details += f" && echo '  {key}: {value}'"
                
                if issue['type'] == 'system_error':
                    details += " && echo '\nRecent System Logs:'"
                    details += " && journalctl --since '10 minutes ago' --no-pager -q | tail -20"
                    
                command = details + " && echo '\nPress Enter to close...' && read"
            
            # Write command file
            with open(filepath, 'w') as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"# MintWatcher {action_type.title()} Command\n")
                f.write(f"# Issue: {issue['title']}\n")
                f.write(f"# Generated: {timestamp}\n\n")
                f.write(command + "\n")
            
            # Make executable
            os.chmod(filepath, 0o755)
            
            print(f"\n=== TERMINAL LAUNCH FAILED ===")
            print(f"Command saved to: {filepath}")
            print(f"To run manually: bash {filepath}")
            print(f"Or open terminal and run: {command}")
            print(f"====================\n")
            
        except Exception as e:
            print(f"Failed to create command file: {e}")
