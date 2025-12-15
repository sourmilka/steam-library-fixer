"""
Steam Library Fixer - Utility Functions
Provides common utility functions used across the application.
"""

import os
import platform
import psutil
from pathlib import Path
from typing import Optional


def is_steam_running() -> bool:
    """
    Check if Steam is currently running.
    
    Returns:
        bool: True if Steam is running, False otherwise
    """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'steam' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_default_steam_path() -> Optional[Path]:
    """
    Get the default Steam installation path for the current platform.
    
    Returns:
        Optional[Path]: Path to Steam directory or None if not found
    """
    system = platform.system()
    
    if system == "Windows":
        # Check common Windows installation paths
        paths = [
            Path("C:/Program Files (x86)/Steam"),
            Path("C:/Program Files/Steam"),
            Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Steam",
            Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Steam",
        ]
    elif system == "Linux":
        home = Path.home()
        paths = [
            home / ".steam" / "steam",
            home / ".local" / "share" / "Steam",
            Path("/usr/share/steam"),
        ]
    elif system == "Darwin":  # macOS
        paths = [
            Path.home() / "Library" / "Application Support" / "Steam",
        ]
    else:
        return None
    
    for path in paths:
        if path.exists() and path.is_dir():
            steamapps = path / "steamapps"
            if steamapps.exists():
                return path
    
    return None


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable format.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        str: Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def safe_path(path: str) -> Path:
    """
    Convert string path to Path object safely.
    
    Args:
        path: String path (may contain escaped backslashes)
        
    Returns:
        Path: Pathlib Path object
    """
    # Handle escaped backslashes from VDF files
    clean_path = path.replace('\\\\', '/')
    return Path(clean_path)


def validate_steam_directory(path: Path) -> bool:
    """
    Validate if a directory is a valid Steam installation.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if valid Steam directory
    """
    if not path.exists() or not path.is_dir():
        return False
    
    required_files = ['steamapps']
    required_exe = {
        'Windows': 'steam.exe',
        'Linux': 'steam.sh',
        'Darwin': 'Steam.AppBundle'
    }
    
    # Check for steamapps folder
    if not (path / 'steamapps').exists():
        return False
    
    # Check for Steam executable
    system = platform.system()
    if system in required_exe:
        if not (path / required_exe[system]).exists():
            return False
    
    return True


def get_app_name_from_manifest(manifest_content: dict) -> Optional[str]:
    """
    Extract game name from manifest content.
    
    Args:
        manifest_content: Parsed manifest dictionary
        
    Returns:
        Optional[str]: Game name or None
    """
    try:
        return manifest_content.get('AppState', {}).get('name')
    except (AttributeError, KeyError):
        return None


def get_app_id_from_filename(filename: str) -> Optional[str]:
    """
    Extract app ID from manifest filename.
    
    Args:
        filename: Manifest filename (e.g., "appmanifest_3564740.acf")
        
    Returns:
        Optional[str]: App ID or None
    """
    try:
        if filename.startswith('appmanifest_') and filename.endswith('.acf'):
            return filename.replace('appmanifest_', '').replace('.acf', '')
    except:
        pass
    return None


def ensure_directory(path: Path) -> bool:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        bool: True if directory exists or was created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False
