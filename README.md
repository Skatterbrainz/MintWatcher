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
cd /home/ds0934/Documents/GitHub/MintWatcher
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

**Quick Start**: Run `./mintwatcher.py --check` to scan your system for issues.

### Basic Commands
```bash
# Show help
./mintwatcher.py --help

# Check system for issues
./mintwatcher.py --check

# Diagnose a specific issue (e.g., issue #2 from --check output)
./mintwatcher.py --diagnose 2

# Show version
./mintwatcher.py --version
```

### Configuration
Edit `config.yaml` to customize:
- **Monitoring thresholds**: CPU, memory, disk usage limits
- **Check intervals**: How often to check system status
- **Exclusions**: Processes and patterns to ignore
- **Warp integration**: Investigation prompt templates

### Example Workflow
1. Run `./mintwatcher.py --check` to scan your system
2. Review the numbered list of issues with severity levels
3. Choose an issue to investigate (e.g., issue #2)
4. Run `./mintwatcher.py --diagnose 2`
5. MintWatcher creates an investigation script at `~/MintWatcher_Commands/`
6. Script automatically opens in your editor
7. Run the script: `bash ~/MintWatcher_Commands/investigate_*.sh`
8. Warp Terminal launches with AI-powered diagnostics

**Output Examples:**

```bash
$ ./mintwatcher.py --check

⚠ Found 2 issue(s):

1. [WARNING] High CPU Usage (85.2%)
   System CPU usage is 85.2%, mainly caused by chrome
   Process: chrome | CPU: 85.2%

2. [WARNING] High Memory Usage (87.5%)
   System memory usage is 87.5%, top process: firefox (2048MB)
   Process: firefox | Memory: 2048MB

To diagnose an issue, run: ./mintwatcher.py --diagnose <number>
```

**File Locations**:
- Investigation scripts: `~/MintWatcher_Commands/investigate_*.sh`

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

MintWatcher is now available on GitHub! Other Linux Mint users can install it easily:

### Option 1: Clone from GitHub (Recommended)
```bash
cd ~/Documents/GitHub
git clone https://github.com/<your-username>/MintWatcher.git
cd MintWatcher
chmod +x setup.sh
./setup.sh
```

### Option 2: Download as Archive
```bash
wget https://github.com/<your-username>/MintWatcher/archive/main.zip
unzip main.zip
cd MintWatcher-main
chmod +x setup.sh
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