# Changelog

All notable changes to MintWatcher will be documented in this file.

## [1.0.0] - 2025-12-18

### Added
- Initial release of MintWatcher
- Real-time system monitoring for Linux Mint
- CPU, memory, and disk usage monitoring
- Process monitoring with suspicious process detection
- System log monitoring with journalctl integration
- Desktop notifications with interactive buttons
- Three-button notification system:
  - **Ignore**: Add issues to exclusion list
  - **Show**: Display issue details in terminal
  - **Investigate**: Launch Warp Terminal with AI diagnostics
- Warp Terminal integration for AI-powered investigation
- Configurable YAML-based settings
- Customizable monitoring thresholds
- Exclusion lists for false positives
- Terminal window launching with multiple fallback methods
- Automatic script file generation when terminal launch fails
- Command file fallback system (`~/MintWatcher_Commands/`)
- CLI interface with multiple commands:
  - `--version`: Show version information
  - `--status`: Display current monitoring status
  - `--start`: Start monitoring in foreground
  - `--enable`/`--disable`: Service management (future)
- Comprehensive test suite:
  - `test_monitoring.py`: Basic monitoring tests
  - `test_warp_integration.py`: Warp Terminal integration tests
  - `test_show_functionality.py`: Show button tests
  - `test_fallback.py`: Fallback system tests
- Documentation:
  - README.md with installation and usage instructions
  - CONTRIBUTING.md with development guidelines
  - LICENSE (MIT)
  - setup.sh for easy installation

### Features in Detail

#### Monitoring Capabilities
- CPU usage threshold detection
- Memory usage monitoring
- Disk space warnings
- Process-level resource tracking
- Suspicious process pattern matching
- System log error detection
- Configurable check intervals

#### Notification System
- libnotify-based desktop notifications
- Action buttons with callbacks
- Issue deduplication to prevent spam
- Severity-based icons (critical, warning, info)
- Configurable timeout settings

#### Warp Integration
- Context-aware investigation prompts
- Automatic prompt formatting with issue data
- Multiple terminal launch methods
- Fallback to executable script files
- Detailed error logging and debugging

#### Configuration
- YAML-based configuration file
- Monitoring thresholds (CPU, memory, disk)
- Check interval settings
- Process exclusion lists
- Log pattern exclusions
- Custom investigation prompt templates
- Daemon settings (PID file, log file)

### Technical Details
- Built with Python 3.6+
- Dependencies: psutil, PyYAML, PyGObject
- Compatible with Linux Mint Cinnamon desktop
- Uses GObject Introspection for notifications
- Subprocess-based terminal launching
- Temporary script file creation for reliability

### Known Issues
- Terminal launching from notification callbacks may not work in all environments
  - Workaround: Fallback script files are created automatically
- Warp Terminal integration requires Warp to be installed and in PATH
- Some notification features may vary by desktop environment

### Future Enhancements
- Systemd service integration for auto-start
- Network monitoring capabilities
- Temperature monitoring
- Battery status monitoring (for laptops)
- Email/webhook notifications
- Web dashboard interface
- Historical metrics tracking
- Customizable notification sounds
