# Steam Library Fixer - Example Usage

## Basic Usage

### Interactive Mode (Recommended)
```bash
python -m src.main
```

This will:
1. Automatically detect your Steam installation
2. Scan for issues
3. Show you what's wrong
4. Let you choose how to fix it

### Command Line Mode

#### Scan Only
```bash
python -m src.main --scan
```

Shows issues without fixing anything.

#### Auto-Fix All Issues
```bash
python -m src.main --fix-all
```

Automatically fixes all detected issues.

#### Dry Run
```bash
python -m src.main --dry-run
```

Shows what would be fixed without making changes.

#### Custom Steam Path
```bash
python -m src.main --steam-path "D:\Games\Steam"
```

### Backup Management

#### List Backups
```bash
python -m src.main --list-backups
```

#### Restore Backup
```bash
python -m src.main --restore backup_20231215_143022
```

## Real-World Examples

### Example 1: Game Downloads to Wrong Drive

**Problem:** Moved "Where Winds Meet" from D: to C:, but updates still download to D:

**Solution:**
```bash
python -m src.main --fix-all
```

**What it fixes:**
- Changes `StagingFolder` from "1" to "0" in the game's manifest
- Cleans up partial downloads on D: drive
- Removes D: library if it's no longer needed

### Example 2: Multiple Games Affected

**Problem:** Moved entire Steam library, many games have issues

**Solution:**
```bash
# First, see what needs fixing
python -m src.main --scan

# Then fix everything
python -m src.main --fix-all
```

### Example 3: Cautious Fixing

**Problem:** Want to see exactly what will change before applying

**Solution:**
```bash
# Dry run to see changes
python -m src.main --dry-run

# If happy with changes, apply them
python -m src.main --fix-all
```

### Example 4: Something Went Wrong

**Problem:** Fixed issues but Steam won't start

**Solution:**
```bash
# List available backups
python -m src.main --list-backups

# Restore the most recent backup
python -m src.main --restore backup_20231215_143022
```

## Advanced Usage

### With Verbose Logging
```bash
python -m src.main --verbose --fix-all
```

### Multiple Operations
```bash
# Scan, review, then fix
python -m src.main --scan
# Review the issues
python -m src.main --fix-all
# Check backups
python -m src.main --list-backups
```

## Troubleshooting

### "Steam is running" Error
```bash
# Close Steam first
taskkill /F /IM steam.exe

# Then run fixer
python -m src.main --fix-all
```

### "Permission Denied" Error
```bash
# Run as Administrator (Windows)
# Right-click PowerShell/CMD -> Run as Administrator
python -m src.main --fix-all
```

### Can't Find Steam
```bash
python -m src.main --steam-path "C:\Program Files (x86)\Steam"
```
