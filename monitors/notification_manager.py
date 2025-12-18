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
        """Send a desktop notification for an issue"""
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
            
        # Create notification
        notification = Notify.Notification.new(
            issue['title'],
            issue['message'],
            self._get_icon_for_severity(issue['severity'])
        )
        
        # Set timeout
        notification.set_timeout(self.config['notifications']['timeout'])
        
        # Add action buttons
        notification.add_action(
            "ignore", "Ignore", 
            self._ignore_callback, 
            (issue, issue_id)
        )
        notification.add_action(
            "show", "Show", 
            self._show_callback, 
            (issue, issue_id)
        )
        notification.add_action(
            "investigate", "Investigate", 
            self._investigate_callback, 
            (issue, issue_id)
        )
        
        # Set up cleanup when notification is closed
        notification.connect('closed', self._notification_closed, issue_id)
        
        # Show notification
        try:
            notification.show()
            self.active_notifications[issue_id] = notification
            print(f"Sent notification: {issue['title']}")
        except Exception as e:
            print(f"Failed to send notification: {e}")
            
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
        
    def _ignore_callback(self, notification, action, user_data):
        """Handle 'Ignore' button click"""
        issue, issue_id = user_data
        
        print(f"Ignoring issue: {issue['title']}")
        
        # Add to exclusions based on issue type
        self._add_to_exclusions(issue)
        
        # Close notification
        notification.close()
        
    def _show_callback(self, notification, action, user_data):
        """Handle 'Show' button click"""
        issue, issue_id = user_data
        
        print(f"Showing details for issue: {issue['title']}")
        
        # Show issue details in terminal
        success = self._show_issue_details(issue)
        
        if not success:
            # Fallback: create a command file
            self._create_command_file(issue, "show")
        
        # Close notification
        notification.close()
        
    def _investigate_callback(self, notification, action, user_data):
        """Handle 'Investigate' button click"""
        issue, issue_id = user_data
        
        print(f"Investigating issue: {issue['title']}")
        
        # Launch Warp Terminal with investigation prompt
        success = self._launch_warp_investigation(issue)
        
        if not success:
            # Fallback: create a command file
            self._create_command_file(issue, "investigate")
        
        # Close notification
        notification.close()
        
    def _notification_closed(self, notification, issue_id):
        """Clean up when notification is closed"""
        if issue_id in self.active_notifications:
            del self.active_notifications[issue_id]
            
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
        """Launch Warp Terminal with investigation prompt"""
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
            return self._launch_terminal_command(warp_command, 'agent', 'run', '--prompt', prompt)
            
        except Exception as e:
            print(f"Failed to launch investigation terminal: {e}")
            print(f"Investigation prompt: {prompt}")
            return False
            
    def _show_issue_details(self, issue):
        """Show issue details in terminal window"""
        issue_type = issue['type']
        issue_data = issue.get('data', {})
        
        # Create detailed display of the issue
        details = f"MintWatcher Issue Details:\n\n"
        details += f"Type: {issue_type}\n"
        details += f"Severity: {issue['severity']}\n"
        details += f"Title: {issue['title']}\n"
        details += f"Message: {issue['message']}\n\n"
        
        if issue_data:
            details += "Additional Data:\n"
            for key, value in issue_data.items():
                details += f"  {key}: {value}\n"
        
        # For log errors, show recent logs
        if issue_type == 'system_error':
            details += "\n" + "="*50 + "\n"
            details += "Recent System Logs:\n"
            details += "="*50 + "\n"
            
        try:
            # Create a command to display the details
            display_cmd = f'echo "{details}"; '
            
            if issue_type == 'system_error':
                # Add command to show recent logs
                display_cmd += 'echo "\nFetching recent system logs..."; '
                display_cmd += 'journalctl --since "10 minutes ago" --no-pager -q | tail -20; '
                
            display_cmd += 'echo "\nPress Enter to close..."; read'
            
            return self._launch_terminal_command('bash', '-c', display_cmd)
            
        except Exception as e:
            print(f"Failed to show issue details: {e}")
            return False
            
    def _launch_terminal_command(self, *args):
        """Launch a command in a new terminal window"""
        import tempfile
        import os
        import stat
        
        # Convert args to a single command string
        cmd_str = ' '.join(f"'{arg}'" if ' ' in str(arg) else str(arg) for arg in args)
        
        print(f"Creating script for terminal command: {cmd_str}")
        
        try:
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as script_file:
                script_content = f"""#!/bin/bash
echo "MintWatcher Terminal Session"
echo "=============================="
echo ""
{cmd_str}
echo ""
echo "Press Enter to close this window..."
read
# Clean up the script file
rm "$0"
"""
                script_file.write(script_content)
                script_path = script_file.name
            
            # Make script executable
            os.chmod(script_path, stat.S_IRWXU)
            
            print(f"Created script: {script_path}")
            
            # Try different methods to launch terminal
            launch_attempts = [
                # Method 1: Direct gnome-terminal
                ['gnome-terminal', '--', 'bash', script_path],
                
                # Method 2: Using nohup to detach completely
                ['nohup', 'gnome-terminal', '--', 'bash', script_path],
                
                # Method 3: Using setsid for session management
                ['setsid', 'gnome-terminal', '--', 'bash', script_path],
                
                # Method 4: Alternative terminals
                ['x-terminal-emulator', '-e', 'bash', script_path],
                ['xterm', '-e', 'bash', script_path],
                
                # Method 5: Desktop file approach (most reliable for notifications)
                self._create_desktop_launcher(script_path)
            ]
            
            for i, cmd in enumerate(launch_attempts):
                if cmd is None:  # Skip None results
                    continue
                    
                try:
                    print(f"Launch attempt {i+1}: {cmd[0] if isinstance(cmd, list) else 'desktop-file'}")
                    
                    if isinstance(cmd, list):
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True
                        )
                        print(f"Process started with PID {process.pid}")
                        return True
                    else:
                        # Desktop file launch
                        result = subprocess.run(cmd, check=False)
                        if result.returncode == 0:
                            print("Desktop launcher executed successfully")
                            return True
                    
                except FileNotFoundError:
                    print(f"Command not found: {cmd[0] if isinstance(cmd, list) else cmd}")
                    continue
                except Exception as e:
                    print(f"Launch failed: {e}")
                    continue
            
            print("All launch attempts failed")
            print(f"Manual execution: bash {script_path}")
            return False
            
        except Exception as e:
            print(f"Failed to create terminal script: {e}")
            print(f"Manual command: {cmd_str}")
            return False
            
    def _create_desktop_launcher(self, script_path):
        """Create a desktop file to launch the script (most reliable method)"""
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.desktop', delete=False) as desktop_file:
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=MintWatcher Action
Exec=gnome-terminal -- bash {script_path}
NoDisplay=true
StartupNotify=false
"""
                desktop_file.write(desktop_content)
                desktop_path = desktop_file.name
            
            # Make desktop file executable
            os.chmod(desktop_path, 0o755)
            
            return ['gtk-launch', os.path.basename(desktop_path.replace('.desktop', ''))]
            
        except Exception as e:
            print(f"Failed to create desktop launcher: {e}")
            return None
            
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
