# MintWatcher

A Linux Mint system monitor that provides desktop notifications for performance and security issues, with interactive "Ignore" and "Investigate" buttons that integrate with Warp Terminal.

## Features

- **Real-time monitoring**: CPU, memory, disk usage, and process monitoring
- **Interactive notifications**: Desktop popups with Ignore/Investigate buttons
- **Warp Terminal integration**: "Investigate" button launches Warp with diagnostic prompts
- **Configurable exclusions**: Ignore false positives automatically
- **System log monitoring**: Detect errors in system logs
- **CLI-only interface**: No GUI required, perfect for server environments

## Installation

### Quick Setup
```bash
cd /home/ds0934/Documents/MintWatcher
chmod +x setup.sh
./setup.sh
```

### Manual Installation
```bash
# Install system dependencies
sudo apt install python3 python3-pip python3-gi python3-gi-cairo gir1.2-notify-0.7

# Install Python dependencies
pip3 install --user -r requirements.txt

# Make executable
chmod +x mintwatcher.py
```

## Usage

### Basic Commands
```bash
# Show help
./mintwatcher.py --help

# Check current status
./mintwatcher.py --status

# Start monitoring (foreground)
./mintwatcher.py --start

# Show version
./mintwatcher.py --version
```

### Configuration
Edit `config.yaml` to customize:
- **Monitoring thresholds**: CPU, memory, disk usage limits
- **Check intervals**: How often to check system status
- **Exclusions**: Processes and patterns to ignore
- **Warp integration**: Investigation prompt templates

### Interactive Notifications
When issues are detected, desktop notifications appear with three buttons:
- **Ignore**: Adds the issue to exclusions list (won't alert again)
- **Show**: Opens terminal window displaying issue details and relevant system logs
- **Investigate**: Launches Warp Terminal with diagnostic prompt for AI-powered investigation

## Configuration Options

### Monitoring Thresholds
```yaml
monitoring:
  cpu_threshold: 80      # CPU usage percentage
  memory_threshold: 85   # Memory usage percentage
  disk_threshold: 90     # Disk usage percentage
  check_interval: 30     # Seconds between checks
```

### Exclusions
```yaml
exclusions:
  processes: ["chrome", "firefox"]    # Processes to ignore
  cpu_spikes: ["compile-process"]     # Processes allowed high CPU
  log_patterns: ["known-error"]       # Log patterns to ignore
```

### Warp Integration
```yaml
warp:
  terminal_command: "warp-terminal"
  investigation_prompts:
    high_cpu: "Investigate high CPU usage by process {process_name}"
    high_memory: "Analyze memory usage by process {process_name}"
```

## System Requirements

- Linux Mint (Cinnamon desktop environment)
- Python 3.6+
- libnotify (for desktop notifications)
- Warp Terminal (for investigation features)

## Monitored Issues

- **High CPU usage**: Detects processes consuming excessive CPU
- **High memory usage**: Identifies memory-hungry processes
- **Disk space warnings**: Alerts when filesystems are nearly full
- **Suspicious processes**: Flags potentially malicious processes
- **System log errors**: Monitors journalctl for system errors

## Sharing with Other Users

To share MintWatcher with other Linux Mint users:

1. **Archive the project**: 
   ```bash
   tar -czf mintwatcher.tar.gz MintWatcher/
   ```

2. **Recipients can extract and run**:
   ```bash
   tar -xzf mintwatcher.tar.gz
   cd MintWatcher
   ./setup.sh
   ```

3. **Or clone from repository** (if published to Git):
   ```bash
   git clone <repository-url>
   cd MintWatcher
   ./setup.sh
   ```

## Troubleshooting

### Notifications not showing
- Ensure `gir1.2-notify-0.7` is installed
- Check if notification daemon is running
- Verify desktop environment supports libnotify

### Warp integration not working
- Ensure Warp Terminal is installed and in PATH
- Try different terminal commands in config
- Check Warp Terminal command-line options

### Permission errors
- Run with appropriate permissions for system monitoring
- Some features may require elevated privileges

## License

Open source - feel free to modify and distribute.