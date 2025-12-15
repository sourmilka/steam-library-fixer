# Steam Library Fixer - Troubleshooting Guide

## Common Issues

### Issue: "Steam is currently running"
**Solution:** Close Steam completely before running the fixer. Check Task Manager to ensure all Steam processes are stopped.

### Issue: "Could not find Steam installation"
**Solution:** 
- Manually specify Steam path: `python -m src.main --steam-path "C:\Program Files (x86)\Steam"`
- Ensure Steam is installed in a standard location

### Issue: "Permission denied" errors
**Solution:**
- Run as Administrator (Windows)
- Ensure you have write permissions to Steam directory
- Close any programs that might be locking Steam files

## How to Restore a Backup

If something goes wrong, you can restore from backup:

```bash
# List available backups
python -m src.main --list-backups

# Restore specific backup
python -m src.main --restore backup_20231215_143022
```

## Manual Fix (If tool doesn't work)

If the automated tool fails, you can manually fix the staging folder issue:

1. Close Steam completely
2. Navigate to `C:\Program Files (x86)\Steam\steamapps\`
3. Find the game's manifest file (e.g., `appmanifest_3564740.acf`)
4. Open with a text editor
5. Find the line with `"StagingFolder"` 
6. Change the value to `"0"`
7. Save and restart Steam

## Reporting Issues

If you encounter a bug:

1. Check the log file in `logs/` directory
2. Create an issue on GitHub with:
   - Error message
   - Log file contents
   - Your OS and Steam version
   - Steps to reproduce

## FAQ

**Q: Is it safe to use?**  
A: Yes! The tool creates backups before making any changes and never deletes game files.

**Q: Will I lose my game saves?**  
A: No, the tool only modifies Steam configuration files, not game data.

**Q: Do I need to reinstall games?**  
A: No, games remain installed and playable.

**Q: Can I undo changes?**  
A: Yes, use the `--restore` command with a backup ID.
