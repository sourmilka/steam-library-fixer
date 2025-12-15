# Contributing to Steam Library Fixer

Thank you for your interest in contributing!

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Use the bug report template
3. Include:
   - OS and Python version
   - Steam version
   - Error messages and logs
   - Steps to reproduce

### Suggesting Features

1. Check existing feature requests
2. Describe the feature and use case
3. Explain how it would help users

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/steam-library-fixer.git
cd steam-library-fixer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
pylint src/
```

## Code Style

- Follow PEP 8
- Use Black for formatting
- Add docstrings to functions
- Keep functions focused and testable
- Add type hints where possible

## Testing

- Write tests for new features
- Ensure existing tests pass
- Test on multiple platforms if possible

## Pull Request Process

1. Update README if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Request review from maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue or discussion on GitHub!
