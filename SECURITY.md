# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Steam Library Fixer, please send an email to the maintainers. All security vulnerabilities will be promptly addressed.

**Please do not report security vulnerabilities through public GitHub issues.**

## Security Considerations

### What This Tool Does
- Reads Steam configuration files (VDF/ACF format)
- Creates backups of configuration files
- Modifies Steam library configuration
- Modifies game manifest files

### What This Tool Does NOT Do
- Access the internet
- Modify game executable files
- Access or transmit personal data
- Run with elevated privileges (unless you explicitly run as admin)
- Modify system files outside Steam directory

### Best Practices
1. Always review the scan results before applying fixes
2. Use `--dry-run` to preview changes
3. Keep backups (automatically created)
4. Run from a trusted source
5. Review the source code (it's open source!)

### File Operations
All file operations are limited to:
- Steam installation directory
- Local backup directory (`./backups`)
- Local log directory (`./logs`)

## Code Review

This is open-source software. You can review all code before running:
- All source code is in the `src/` directory
- No obfuscation or compiled binaries
- Clear, documented Python code
- No external API calls or network operations
