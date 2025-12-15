"""
Steam Library Fixer - Backup Manager Module
Handles backup and restore operations for Steam configuration files.
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class BackupEntry:
    """Represents a single backed up file."""
    original_path: str
    backup_path: str
    timestamp: str
    file_size: int


@dataclass
class BackupManifest:
    """Manifest of a complete backup operation."""
    backup_id: str
    timestamp: str
    steam_path: str
    files: List[BackupEntry]
    description: str


class BackupManager:
    """Manages backups of Steam configuration files."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory for backups (default: ./backups)
        """
        self.backup_dir = backup_dir or Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.current_backup_id: Optional[str] = None
        self.current_backup_path: Optional[Path] = None
    
    def create_backup(self, files: List[Path], description: str = "") -> str:
        """
        Create backup of specified files.
        
        Args:
            files: List of file paths to backup
            description: Description of this backup
            
        Returns:
            str: Backup ID
        """
        # Generate backup ID and create directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)
        
        # Backup each file
        backup_entries = []
        for file_path in files:
            if not file_path.exists():
                continue
            
            # Create backup filename
            backup_filename = file_path.name
            backup_file_path = backup_path / backup_filename
            
            # Copy file
            shutil.copy2(file_path, backup_file_path)
            
            # Create entry
            entry = BackupEntry(
                original_path=str(file_path),
                backup_path=str(backup_file_path),
                timestamp=timestamp,
                file_size=file_path.stat().st_size
            )
            backup_entries.append(entry)
        
        # Create manifest
        manifest = BackupManifest(
            backup_id=backup_id,
            timestamp=timestamp,
            steam_path=str(files[0].parent.parent if files else ""),
            files=backup_entries,
            description=description or f"Backup created at {timestamp}"
        )
        
        # Save manifest
        manifest_path = backup_path / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(manifest), f, indent=2)
        
        self.current_backup_id = backup_id
        self.current_backup_path = backup_path
        
        return backup_id
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore files from a backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            bool: True if successful
        """
        backup_path = self.backup_dir / backup_id
        manifest_path = backup_path / "manifest.json"
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Backup manifest not found: {manifest_path}")
        
        # Load manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        manifest = BackupManifest(**manifest_data)
        
        # Restore each file
        for entry_data in manifest.files:
            entry = BackupEntry(**entry_data)
            backup_file = Path(entry.backup_path)
            original_file = Path(entry.original_path)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Create parent directory if needed
            original_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore file
            shutil.copy2(backup_file, original_file)
        
        return True
    
    def list_backups(self) -> List[BackupManifest]:
        """
        List all available backups.
        
        Returns:
            List[BackupManifest]: List of backup manifests
        """
        backups = []
        
        for backup_dir in sorted(self.backup_dir.iterdir(), reverse=True):
            if not backup_dir.is_dir():
                continue
            
            manifest_path = backup_dir / "manifest.json"
            if not manifest_path.exists():
                continue
            
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                manifest = BackupManifest(**manifest_data)
                backups.append(manifest)
            except Exception:
                continue
        
        return backups
    
    def get_backup(self, backup_id: str) -> Optional[BackupManifest]:
        """
        Get backup manifest by ID.
        
        Args:
            backup_id: Backup ID
            
        Returns:
            Optional[BackupManifest]: Backup manifest or None
        """
        manifest_path = self.backup_dir / backup_id / "manifest.json"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            return BackupManifest(**manifest_data)
        except Exception:
            return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_id: Backup ID to delete
            
        Returns:
            bool: True if successful
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            return False
        
        try:
            shutil.rmtree(backup_path)
            return True
        except Exception:
            return False
    
    def get_latest_backup(self) -> Optional[BackupManifest]:
        """
        Get the most recent backup.
        
        Returns:
            Optional[BackupManifest]: Latest backup or None
        """
        backups = self.list_backups()
        return backups[0] if backups else None
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Delete old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            int: Number of backups deleted
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        deleted = 0
        for backup in backups[keep_count:]:
            if self.delete_backup(backup.backup_id):
                deleted += 1
        
        return deleted
