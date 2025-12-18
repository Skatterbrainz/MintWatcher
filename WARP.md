# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

MintWatcher is a Linux Mint system monitor that provides desktop notifications for performance and security issues. It integrates with Warp Terminal to enable AI-powered investigation of system issues.

**Key capabilities:**
- Real-time monitoring of CPU, memory, disk usage, processes, and system logs
- Interactive terminal prompts when issues are detected
- Creates investigation scripts for Warp Terminal AI
- Configurable exclusions to prevent false positives

## Architecture

### Core Components

**Main orchestrator:** `mintwatcher.py`
- CLI entry point with argument parsing
- Manages daemon lifecycle (start/stop/status)
- Coordinates monitoring loop and notifications
- Handles PID file and signal management

**System monitoring:** `monitors/system_monitor.py`
- `SystemMonitor` class performs all system checks
- Methods: `_check_cpu_usage()`, `_check_memory_usage()`, `_check_disk_usage()`, `_check_processes()`, `_check_system_logs()`
- Returns list of issue dictionaries with type, severity, title, message, and data fields
- Uses `psutil` for system metrics and `journalctl` for log monitoring

**Notification system:** `monitors/notification_manager.py`
- `NotificationManager` class handles desktop notifications and terminal prompts
- Uses `gi.repository.Notify` (libnotify) for desktop popups
- Interactive terminal workflow: Show details / Create investigation script / Add to exclusions
- Creates two types of output files:
  - Issue reports: `~/MintWatcher_Reports/mintwatcher_issue_*.txt`
  - Investigation scripts: `~/MintWatcher_Commands/investigate_*.sh`

**Configuration:** `config.yaml`
- Monitoring thresholds and intervals
- Process/pattern exclusions
- Warp investigation prompt templates (use Python `.format()` syntax)
- Daemon settings (PID file location)

### Data Flow

1. Main loop in `mintwatcher.py` calls `monitor.check_system()` every `check_interval` seconds
2. `SystemMonitor` runs all enabled checks and returns list of issues
3. For each issue, `NotificationManager.send_notification()` is called
4. Manager checks exclusions, shows desktop notification, and prompts in terminal
5. User can ignore (adds to config exclusions), show details, or create investigation script
6. Investigation scripts use `warp-terminal agent run --prompt` to launch AI diagnostics

### Issue Structure

All issues follow this schema:
```python
{
    'type': 'high_cpu' | 'high_memory' | 'disk_space' | 'suspicious_process' | 'system_error',
    'severity': 'critical' | 'warning' | 'info',
    'title': 'Human-readable title',
    'message': 'Detailed message',
    'data': {
        # Type-specific fields like process_name, cpu_percent, memory_mb, etc.
    }
}
```

## Common Development Tasks

### Running and Testing

```bash
# Start monitoring (foreground with output)
./mintwatcher.py --start

# Check status and current metrics
./mintwatcher.py --status

# Stop all instances
./mintwatcher.py --stop

# Run basic monitoring validation
./test_monitoring.py

# Integration test for start/stop
./test_start_stop.sh

# Test specific functionality
./test_warp_integration.py
./test_show_functionality.py
./test_fallback.py
```

### Setup and Installation

```bash
# Quick setup (runs all installation steps)
./setup.sh

# Manual installation
sudo apt install python3 python3-pip python3-gi python3-gi-cairo gir1.2-notify-0.7
pip3 install --user -r requirements.txt
chmod +x mintwatcher.py
```

### Modifying Behavior

**Add new check type:**
1. Add method to `SystemMonitor` following `_check_*()` pattern
2. Call from `check_system()` method
3. Add investigation prompt template to `config.yaml` under `warp.investigation_prompts`
4. Handle new type in `NotificationManager._add_to_exclusions()` if needed

**Change notification behavior:**
- Edit `NotificationManager._terminal_prompt()` for interaction flow
- Modify `_show_issue_details()` or `_launch_warp_investigation()` for action handlers

**Adjust thresholds or exclusions:**
- Edit `config.yaml` (changes persist)
- Or use "Ignore" action when notification appears (automatically updates config)

## Important Notes

### System Dependencies
- Requires Linux Mint with Cinnamon desktop (uses libnotify)
- Python 3.6+ with `psutil`, `PyYAML`, `PyGObject`
- Warp Terminal must be in PATH as `warp-terminal`
- System commands used: `journalctl`, `ps`

### PID Management
- PID file location: `/tmp/mintwatcher.pid` (configurable in `config.yaml`)
- `--stop` command kills processes by PID file and `ps aux` search
- Handles stale PID files automatically

### Warp Integration
- Investigation scripts call: `warp-terminal agent run --prompt '<prompt>'`
- Prompts use Python format strings with issue data: `{process_name}`, `{cpu_percent}`, etc.
- Scripts are saved to `~/MintWatcher_Commands/` as executable `.sh` files
- Opens in `xed` or falls back to `xdg-open`

### Threading Model
- Main thread waits on signal handlers
- `_monitoring_loop()` runs in daemon thread
- No complex synchronization needed (read-only config access from monitoring thread)

### Exclusion Logic
- Exclusions prevent notifications entirely (checked in `_is_excluded()`)
- Three exclusion lists: `processes`, `cpu_spikes`, `log_patterns`
- High CPU checks both `processes` and `cpu_spikes` lists
- Adding exclusion saves config immediately via `_save_config()`
