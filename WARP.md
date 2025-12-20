# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

MintWatcher is a Linux Mint system monitor that provides one-shot system checks with numbered issue reporting. It integrates with Warp Terminal to enable AI-powered investigation of system issues.

**Key capabilities:**
- On-demand system checks (CPU, memory, disk, processes, system logs)
- Numbered issue listing with severity indicators
- Creates investigation scripts for Warp Terminal AI
- Configurable thresholds and exclusions

## Architecture

### Core Components

**Main orchestrator:** `mintwatcher.py`
- CLI entry point with argument parsing (`--check`, `--diagnose`, `--version`)
- One-shot execution model (runs and exits)
- Caches issues to `/tmp/mintwatcher_last_check.json` for diagnose command
- Creates investigation scripts at `~/MintWatcher_Commands/`

**System monitoring:** `monitors/system_monitor.py`
- `SystemMonitor` class performs all system checks
- Methods: `_check_cpu_usage()`, `_check_memory_usage()`, `_check_disk_usage()`, `_check_processes()`, `_check_system_logs()`
- Returns list of issue dictionaries with type, severity, title, message, and data fields
- Uses `psutil` for system metrics and `journalctl` for log monitoring

**Issue caching:** JSON-based cache system
- Issues from `--check` are cached to `/tmp/mintwatcher_last_check.json`
- Cache includes timestamp and full issue data
- `--diagnose` command reads from cache to generate scripts
- Cache cleared when no issues found

**Configuration:** `config.yaml`
- Monitoring thresholds and intervals
- Process/pattern exclusions
- Warp investigation prompt templates (use Python `.format()` syntax)
- Daemon settings (PID file location)

### Data Flow

**Check workflow:**
1. User runs `./mintwatcher.py --check`
2. `MintWatcher.check_system()` calls `monitor.check_system()`
3. `SystemMonitor` runs all enabled checks and returns list of issues
4. Issues are cached to JSON file with timestamp
5. Issues displayed with numbers, severity colors, and key data points
6. Command exits after displaying results

**Diagnose workflow:**
1. User runs `./mintwatcher.py --diagnose N` where N is issue number
2. `MintWatcher.diagnose_issue()` loads cached issues from JSON
3. Selected issue is used to generate investigation script
4. Script created at `~/MintWatcher_Commands/investigate_*.sh`
5. Script uses Warp prompt template from config with issue data interpolated
6. Script auto-opens in `xed` editor for review
7. User runs script to launch `warp-terminal agent run --prompt`

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
# Check system for issues
./mintwatcher.py --check

# Diagnose specific issue (e.g., issue #2)
./mintwatcher.py --diagnose 2

# Show version
./mintwatcher.py --version

# Run basic monitoring validation
./test_monitoring.py
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
4. Update issue type enum in docstring/comments

**Change output formatting:**
- Edit `MintWatcher.check_system()` to modify how issues are displayed
- Color codes in `_get_color_for_severity()` method
- Key info extraction logic determines what data appears in summary

**Adjust thresholds or exclusions:**
- Edit `config.yaml` directly (all changes are manual now)

## Important Notes

### System Dependencies
- Requires Linux Mint with Cinnamon desktop (uses libnotify)
- Python 3.6+ with `psutil`, `PyYAML`, `PyGObject`
- Warp Terminal must be in PATH as `warp-terminal`
- System commands used: `journalctl`, `ps`

### Issue Caching
- Cache file: `/tmp/mintwatcher_last_check.json`
- Contains timestamp and array of issue objects
- Automatically cleared when no issues detected
- Required for `--diagnose` command to work

### Warp Integration
- Investigation scripts call: `warp-terminal agent run --prompt '<prompt>'`
- Prompts use Python format strings with issue data: `{process_name}`, `{cpu_percent}`, etc.
- Scripts are saved to `~/MintWatcher_Commands/` as executable `.sh` files
- Opens in `xed` or falls back to `xdg-open`

### Execution Model
- Single-threaded, synchronous execution
- No daemon or background processes
- Each invocation runs checks and exits immediately
- No signal handlers or state management needed

### Exclusion Logic
- Exclusions filter issues in `SystemMonitor` before returning to main script
- Three exclusion lists in config: `processes`, `cpu_spikes`, `log_patterns`
- High CPU checks both `processes` and `cpu_spikes` lists
- Exclusions must be added manually to `config.yaml`
