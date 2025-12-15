# Quick Start Guide

## Installation

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed:
```bash
python --version
```

### Step 2: Install Dependencies
```bash
cd steam-library-fixer
pip install -r requirements.txt
```

### Step 3: Run the Tool
```bash
python -m src.main
```

## First Time Use

1. **Close Steam** - The tool will remind you, but it's important!

2. **Run Scan** - The tool automatically scans your Steam installation

3. **Review Issues** - See what problems were found

4. **Apply Fixes** - Choose to fix all or review individually

5. **Restart Steam** - Your issues should now be resolved!

## Common Commands

```bash
# Interactive mode (easiest)
python -m src.main

# Just scan, don't fix
python -m src.main --scan

# Fix everything automatically
python -m src.main --fix-all

# Preview fixes without applying
python -m src.main --dry-run

# See available backups
python -m src.main --list-backups
```

## What Gets Fixed?

✓ Games downloading to wrong drives  
✓ Orphaned download files  
✓ Dead library configurations  
✓ Staging folder mismatches  
✓ Missing library paths  

## Safety

- ✅ Creates backups automatically
- ✅ Never deletes game files
- ✅ Can restore previous state
- ✅ Shows what will change (dry-run)
- ✅ Detailed logs for troubleshooting

## Need Help?

- Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- See [EXAMPLES.md](docs/EXAMPLES.md) for usage examples
- Open an issue on GitHub
