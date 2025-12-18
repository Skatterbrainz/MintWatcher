# Contributing to MintWatcher

Thank you for your interest in contributing to MintWatcher! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/MintWatcher.git
   cd MintWatcher
   ```
3. Install development dependencies:
   ```bash
   ./setup.sh
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines for Python code
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Testing
Before submitting a pull request, test your changes:
```bash
# Test basic monitoring
python3 test_monitoring.py

# Test Warp integration
python3 test_warp_integration.py

# Test Show functionality
python3 test_show_functionality.py

# Test fallback behavior
python3 test_fallback.py
```

### Project Structure
```
MintWatcher/
├── mintwatcher.py          # Main CLI entry point
├── config.yaml             # Configuration file
├── monitors/               # Monitoring modules
│   ├── __init__.py
│   ├── system_monitor.py   # System monitoring logic
│   └── notification_manager.py  # Notification handling
├── tests/                  # Test scripts
└── README.md
```

## Adding New Monitors

To add a new type of monitoring:

1. Add monitoring logic in `monitors/system_monitor.py`:
   ```python
   def _check_new_feature(self):
       """Check for new feature"""
       issues = []
       # Your monitoring logic here
       return issues
   ```

2. Add check to `check_system()` method:
   ```python
   def check_system(self):
       issues = []
       issues.extend(self._check_new_feature())
       return issues
   ```

3. Add configuration options to `config.yaml`:
   ```yaml
   monitoring:
     new_feature_threshold: 80
   ```

4. Add investigation prompt template:
   ```yaml
   warp:
     investigation_prompts:
       new_feature: "Investigate {issue_description}..."
   ```

## Submitting Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub

### Commit Message Guidelines
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep first line under 50 characters
- Add detailed description if needed

Examples:
```
Add disk I/O monitoring feature
Fix notification button callback handling
Update README with installation instructions
```

## Reporting Issues

When reporting bugs, please include:
- Linux Mint version
- Python version
- Full error message or log output
- Steps to reproduce the issue
- Expected vs actual behavior

## Feature Requests

Feature requests are welcome! Please:
- Check if the feature already exists or is planned
- Describe the use case clearly
- Explain how it would benefit users
- Consider implementation complexity

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## Questions?

Feel free to open an issue for questions or discussions about:
- Feature ideas
- Implementation approaches
- Usage questions
- Documentation improvements

## License

By contributing to MintWatcher, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).
