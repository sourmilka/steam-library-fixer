"""
Steam Library Fixer - Logger Module
Provides logging functionality with file and console output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler


class SteamFixerLogger:
    """Custom logger for Steam Library Fixer with rich formatting."""
    
    def __init__(self, log_dir: Optional[Path] = None, verbose: bool = False):
        """
        Initialize logger with file and console handlers.
        
        Args:
            log_dir: Directory for log files (default: ./logs)
            verbose: Enable verbose/debug logging
        """
        self.console = Console()
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("SteamLibraryFixer")
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler - always detailed
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"steam_fixer_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler - with rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=False,
            show_path=False,
            markup=True
        )
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        self.logger.addHandler(console_handler)
        
        self.log_file_path = log_file
        self.logger.info(f"Logging to: {log_file}")
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def success(self, message: str):
        """Log success message with green color."""
        self.console.print(f"[green]✓[/green] {message}")
        self.logger.info(f"SUCCESS: {message}")
    
    def heading(self, message: str):
        """Print a heading/section title."""
        self.console.print(f"\n[bold cyan]{message}[/bold cyan]")
        self.logger.info(f"=== {message} ===")
    
    def separator(self):
        """Print a separator line."""
        self.console.print("─" * 60)
    
    def get_log_path(self) -> Path:
        """Get current log file path."""
        return self.log_file_path


# Global logger instance
_logger: Optional[SteamFixerLogger] = None


def get_logger(log_dir: Optional[Path] = None, verbose: bool = False) -> SteamFixerLogger:
    """
    Get or create global logger instance.
    
    Args:
        log_dir: Directory for log files
        verbose: Enable verbose logging
        
    Returns:
        SteamFixerLogger: Logger instance
    """
    global _logger
    if _logger is None:
        _logger = SteamFixerLogger(log_dir, verbose)
    return _logger
