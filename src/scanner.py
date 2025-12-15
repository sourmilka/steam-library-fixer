"""
Steam Library Fixer - Scanner Module
Scans Steam installation for issues and misconfigurations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Any
from .vdf_parser import VDFParser, read_manifest, read_library_folders
from .utils import safe_path, get_app_name_from_manifest, get_app_id_from_filename


@dataclass
class LibraryInfo:
    """Information about a Steam library folder."""
    library_id: str
    path: Path
    exists: bool
    apps: Dict[str, int]  # app_id -> size


@dataclass
class GameIssue:
    """Represents an issue found with a game installation."""
    app_id: str
    game_name: str
    manifest_path: Path
    issue_type: str
    description: str
    current_value: Any
    expected_value: Any
    severity: str  # "critical", "warning", "info"


@dataclass
class OrphanedDownload:
    """Represents orphaned download files."""
    library_path: Path
    app_id: str
    files: List[Path]
    total_size: int


class SteamScanner:
    """Scans Steam installation for configuration issues."""
    
    def __init__(self, steam_path: Path):
        """
        Initialize scanner with Steam installation path.
        
        Args:
            steam_path: Path to Steam directory
        """
        self.steam_path = steam_path
        self.steamapps_path = steam_path / "steamapps"
        self.library_vdf_path = self.steamapps_path / "libraryfolders.vdf"
        
        self.libraries: Dict[str, LibraryInfo] = {}
        self.games: Dict[str, Dict[str, Any]] = {}
        self.issues: List[GameIssue] = []
        self.orphaned_downloads: List[OrphanedDownload] = []
    
    def scan(self) -> bool:
        """
        Perform complete scan of Steam installation.
        
        Returns:
            bool: True if scan completed successfully
        """
        try:
            self._scan_libraries()
            self._scan_manifests()
            self._detect_issues()
            self._scan_orphaned_downloads()
            return True
        except Exception as e:
            raise RuntimeError(f"Scan failed: {e}")
    
    def _scan_libraries(self):
        """Scan and catalog all Steam library folders."""
        if not self.library_vdf_path.exists():
            raise FileNotFoundError(f"Library config not found: {self.library_vdf_path}")
        
        data = read_library_folders(self.library_vdf_path)
        library_folders = data.get('libraryfolders', {})
        
        for lib_id, lib_data in library_folders.items():
            if isinstance(lib_data, dict) and 'path' in lib_data:
                lib_path = safe_path(lib_data['path'])
                lib_info = LibraryInfo(
                    library_id=lib_id,
                    path=lib_path,
                    exists=lib_path.exists(),
                    apps=lib_data.get('apps', {})
                )
                self.libraries[lib_id] = lib_info
    
    def _scan_manifests(self):
        """Scan all game manifest files in the main Steam library."""
        manifest_files = self.steamapps_path.glob("appmanifest_*.acf")
        
        for manifest_path in manifest_files:
            try:
                app_id = get_app_id_from_filename(manifest_path.name)
                if not app_id:
                    continue
                
                manifest_data = read_manifest(manifest_path)
                app_state = manifest_data.get('AppState', {})
                
                game_info = {
                    'app_id': app_id,
                    'name': app_state.get('name', 'Unknown'),
                    'manifest_path': manifest_path,
                    'install_dir': app_state.get('installdir', ''),
                    'staging_folder': app_state.get('StagingFolder'),
                    'size_on_disk': app_state.get('SizeOnDisk', 0),
                    'manifest_data': manifest_data
                }
                
                self.games[app_id] = game_info
                
            except Exception as e:
                # Log but don't fail on individual manifest errors
                print(f"Warning: Failed to parse {manifest_path.name}: {e}")
    
    def _detect_issues(self):
        """Detect configuration issues with installed games."""
        for app_id, game_info in self.games.items():
            staging_folder = game_info.get('staging_folder')
            
            # Issue 1: Staging folder mismatch
            if staging_folder is not None and staging_folder != '0':
                # Game is in library 0 but staging folder points elsewhere
                target_library = str(staging_folder)
                
                if target_library in self.libraries:
                    target_lib_info = self.libraries[target_library]
                    
                    # Critical if target library doesn't exist
                    if not target_lib_info.exists:
                        self.issues.append(GameIssue(
                            app_id=app_id,
                            game_name=game_info['name'],
                            manifest_path=game_info['manifest_path'],
                            issue_type="missing_staging_library",
                            description=f"Update downloads point to non-existent library at {target_lib_info.path}",
                            current_value=staging_folder,
                            expected_value='0',
                            severity="critical"
                        ))
                    else:
                        # Warning if staging folder differs from install location
                        self.issues.append(GameIssue(
                            app_id=app_id,
                            game_name=game_info['name'],
                            manifest_path=game_info['manifest_path'],
                            issue_type="staging_folder_mismatch",
                            description=f"Game installed in library 0 but updates download to library {staging_folder}",
                            current_value=staging_folder,
                            expected_value='0',
                            severity="warning"
                        ))
    
    def _scan_orphaned_downloads(self):
        """Scan for orphaned download files in all libraries."""
        for lib_id, lib_info in self.libraries.items():
            if not lib_info.exists:
                continue
            
            downloading_path = lib_info.path / "steamapps" / "downloading"
            if not downloading_path.exists():
                continue
            
            # Check for app-specific folders and files
            for item in downloading_path.iterdir():
                if item.is_dir():
                    # Directory named after app_id
                    app_id = item.name
                    if app_id.isdigit():
                        # Check if this game is actually installed in this library
                        if app_id in self.games and lib_id != '0':
                            # Game is in main library but has downloads here
                            files = list(item.rglob("*"))
                            total_size = sum(f.stat().st_size for f in files if f.is_file())
                            
                            self.orphaned_downloads.append(OrphanedDownload(
                                library_path=lib_info.path,
                                app_id=app_id,
                                files=files,
                                total_size=total_size
                            ))
                
                elif item.is_file():
                    # Check for depot or state files
                    if 'depot_' in item.name or 'state_' in item.name:
                        # Extract app_id from filename
                        parts = item.name.split('_')
                        if len(parts) >= 2 and parts[1].isdigit():
                            app_id = parts[1]
                            if app_id in self.games and lib_id != '0':
                                self.orphaned_downloads.append(OrphanedDownload(
                                    library_path=lib_info.path,
                                    app_id=app_id,
                                    files=[item],
                                    total_size=item.stat().st_size
                                ))
    
    def get_issues_by_severity(self, severity: str) -> List[GameIssue]:
        """
        Get issues filtered by severity.
        
        Args:
            severity: "critical", "warning", or "info"
            
        Returns:
            List[GameIssue]: Filtered issues
        """
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get scan summary statistics.
        
        Returns:
            Dict: Summary information
        """
        return {
            'total_libraries': len(self.libraries),
            'active_libraries': sum(1 for lib in self.libraries.values() if lib.exists),
            'total_games': len(self.games),
            'total_issues': len(self.issues),
            'critical_issues': len(self.get_issues_by_severity('critical')),
            'warnings': len(self.get_issues_by_severity('warning')),
            'orphaned_downloads': len(self.orphaned_downloads),
            'orphaned_size': sum(od.total_size for od in self.orphaned_downloads)
        }
    
    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return len(self.issues) > 0 or len(self.orphaned_downloads) > 0
