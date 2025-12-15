"""
Steam Library Fixer - Fixer Module
Applies fixes to Steam configuration issues.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from .scanner import SteamScanner, GameIssue, OrphanedDownload
from .vdf_parser import read_manifest, write_manifest, read_library_folders, write_library_folders
from .backup import BackupManager
from .logger import get_logger
import shutil


class SteamFixer:
    """Applies fixes to Steam configuration issues."""
    
    def __init__(self, scanner: SteamScanner, backup_manager: BackupManager, dry_run: bool = False):
        """
        Initialize fixer.
        
        Args:
            scanner: SteamScanner instance with detected issues
            backup_manager: BackupManager for creating backups
            dry_run: If True, don't actually apply changes
        """
        self.scanner = scanner
        self.backup_manager = backup_manager
        self.dry_run = dry_run
        self.logger = get_logger()
        self.fixed_count = 0
        self.failed_count = 0
    
    def fix_all(self) -> Dict[str, Any]:
        """
        Fix all detected issues.
        
        Returns:
            Dict: Summary of fixes applied
        """
        self.logger.heading("Fixing Issues")
        
        # Create backup first
        if not self.dry_run:
            backup_files = self._collect_files_to_backup()
            if backup_files:
                self.logger.info(f"Creating backup of {len(backup_files)} files...")
                backup_id = self.backup_manager.create_backup(
                    backup_files,
                    "Pre-fix backup"
                )
                self.logger.success(f"Backup created: {backup_id}")
        
        # Fix staging folder issues
        for issue in self.scanner.issues:
            if issue.issue_type in ["staging_folder_mismatch", "missing_staging_library"]:
                self._fix_staging_folder(issue)
        
        # Clean orphaned downloads
        for orphaned in self.scanner.orphaned_downloads:
            self._clean_orphaned_download(orphaned)
        
        # Remove dead libraries (optional)
        dead_libraries = [lib for lib in self.scanner.libraries.values() if not lib.exists]
        if dead_libraries:
            self._remove_dead_libraries(dead_libraries)
        
        return {
            'fixed': self.fixed_count,
            'failed': self.failed_count,
            'dry_run': self.dry_run
        }
    
    def _fix_staging_folder(self, issue: GameIssue) -> bool:
        """
        Fix staging folder mismatch in game manifest.
        
        Args:
            issue: GameIssue to fix
            
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info(f"Fixing {issue.game_name} (App ID: {issue.app_id})")
            self.logger.debug(f"  Issue: {issue.description}")
            self.logger.debug(f"  Current: StagingFolder = {issue.current_value}")
            self.logger.debug(f"  Expected: StagingFolder = {issue.expected_value}")
            
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] Would change StagingFolder from {issue.current_value} to {issue.expected_value}")
                self.fixed_count += 1
                return True
            
            # Read manifest
            manifest_data = read_manifest(issue.manifest_path)
            
            # Update staging folder
            if 'AppState' in manifest_data:
                manifest_data['AppState']['StagingFolder'] = str(issue.expected_value)
            
            # Write back
            if write_manifest(manifest_data, issue.manifest_path):
                self.logger.success(f"  Fixed StagingFolder for {issue.game_name}")
                self.fixed_count += 1
                return True
            else:
                self.logger.error(f"  Failed to write manifest for {issue.game_name}")
                self.failed_count += 1
                return False
                
        except Exception as e:
            self.logger.error(f"  Error fixing {issue.game_name}: {e}")
            self.failed_count += 1
            return False
    
    def _clean_orphaned_download(self, orphaned: OrphanedDownload) -> bool:
        """
        Remove orphaned download files.
        
        Args:
            orphaned: OrphanedDownload to clean
            
        Returns:
            bool: True if successful
        """
        try:
            game_name = self.scanner.games.get(orphaned.app_id, {}).get('name', 'Unknown')
            file_count = len(orphaned.files)
            size_mb = orphaned.total_size / (1024 * 1024)
            
            self.logger.info(f"Cleaning orphaned downloads for {game_name} (App ID: {orphaned.app_id})")
            self.logger.debug(f"  Location: {orphaned.library_path}")
            self.logger.debug(f"  Files: {file_count}, Size: {size_mb:.2f} MB")
            
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] Would delete {file_count} orphaned files ({size_mb:.2f} MB)")
                self.fixed_count += 1
                return True
            
            # Delete files
            for file_path in orphaned.files:
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.warning(f"  Failed to delete {file_path.name}: {e}")
            
            self.logger.success(f"  Cleaned {file_count} orphaned files")
            self.fixed_count += 1
            return True
            
        except Exception as e:
            self.logger.error(f"  Error cleaning orphaned downloads: {e}")
            self.failed_count += 1
            return False
    
    def _remove_dead_libraries(self, dead_libraries: List) -> bool:
        """
        Remove non-existent libraries from Steam configuration.
        
        Args:
            dead_libraries: List of LibraryInfo objects that don't exist
            
        Returns:
            bool: True if successful
        """
        if not dead_libraries:
            return True
        
        try:
            self.logger.info(f"Removing {len(dead_libraries)} dead library entries")
            
            for lib in dead_libraries:
                self.logger.debug(f"  Library {lib.library_id}: {lib.path}")
            
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] Would remove {len(dead_libraries)} library entries")
                self.fixed_count += 1
                return True
            
            # Read library config
            library_data = read_library_folders(self.scanner.library_vdf_path)
            
            # Remove dead libraries
            if 'libraryfolders' in library_data:
                for lib in dead_libraries:
                    if lib.library_id in library_data['libraryfolders']:
                        del library_data['libraryfolders'][lib.library_id]
            
            # Write back
            if write_library_folders(library_data, self.scanner.library_vdf_path):
                self.logger.success(f"  Removed {len(dead_libraries)} dead library entries")
                self.fixed_count += 1
                return True
            else:
                self.logger.error("  Failed to write library configuration")
                self.failed_count += 1
                return False
                
        except Exception as e:
            self.logger.error(f"  Error removing dead libraries: {e}")
            self.failed_count += 1
            return False
    
    def _collect_files_to_backup(self) -> List[Path]:
        """
        Collect all files that will be modified.
        
        Returns:
            List[Path]: Files to backup
        """
        files = set()
        
        # Add library config if we're removing dead libraries
        dead_libraries = [lib for lib in self.scanner.libraries.values() if not lib.exists]
        if dead_libraries:
            files.add(self.scanner.library_vdf_path)
        
        # Add manifest files for games with issues
        for issue in self.scanner.issues:
            files.add(issue.manifest_path)
        
        return list(files)
