"""
Steam Library Fixer - Main Application
Interactive CLI for fixing Steam library issues.
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from .scanner import SteamScanner
from .fixer import SteamFixer
from .backup import BackupManager
from .logger import get_logger
from .utils import (
    get_default_steam_path,
    is_steam_running,
    validate_steam_directory,
    format_bytes
)


console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🎮  STEAM LIBRARY FIXER  🔧                    ║
    ║                                                           ║
    ║     Automatic Steam Configuration Repair Tool            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def check_steam_running() -> bool:
    """Check if Steam is running and prompt to close."""
    if is_steam_running():
        console.print("\n[yellow]⚠ Steam is currently running![/yellow]")
        console.print("Steam must be closed before making configuration changes.")
        
        if Confirm.ask("Would you like to continue anyway? (Not recommended)"):
            return True
        else:
            console.print("[red]Please close Steam and run this tool again.[/red]")
            return False
    return True


def display_scan_results(scanner: SteamScanner):
    """Display scan results in a formatted table."""
    summary = scanner.get_summary()
    
    # Summary panel
    summary_text = f"""
    Total Libraries: {summary['total_libraries']} ({summary['active_libraries']} active)
    Total Games: {summary['total_games']}
    Issues Found: {summary['total_issues']}
    • Critical: {summary['critical_issues']}
    • Warnings: {summary['warnings']}
    Orphaned Downloads: {summary['orphaned_downloads']} ({format_bytes(summary['orphaned_size'])})
    """
    
    console.print(Panel(summary_text, title="[bold]Scan Results[/bold]", border_style="cyan"))
    
    # Issues table
    if scanner.issues:
        console.print("\n[bold]Detected Issues:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Game", style="cyan", width=30)
        table.add_column("Issue Type", style="yellow", width=25)
        table.add_column("Severity", justify="center", width=10)
        table.add_column("Description", width=40)
        
        for issue in scanner.issues:
            severity_style = {
                'critical': '[red]CRITICAL[/red]',
                'warning': '[yellow]WARNING[/yellow]',
                'info': '[blue]INFO[/blue]'
            }.get(issue.severity, issue.severity)
            
            table.add_row(
                issue.game_name[:28] + "..." if len(issue.game_name) > 28 else issue.game_name,
                issue.issue_type.replace('_', ' ').title(),
                severity_style,
                issue.description[:38] + "..." if len(issue.description) > 38 else issue.description
            )
        
        console.print(table)
    
    # Orphaned downloads
    if scanner.orphaned_downloads:
        console.print("\n[bold]Orphaned Downloads:[/bold]")
        
        for orphaned in scanner.orphaned_downloads:
            game_name = scanner.games.get(orphaned.app_id, {}).get('name', 'Unknown')
            console.print(f"  • {game_name} - {len(orphaned.files)} files ({format_bytes(orphaned.total_size)})")


def interactive_mode(steam_path: Path):
    """Run in interactive mode with menu."""
    logger = get_logger(verbose=False)
    
    print_banner()
    
    # Check Steam
    if not check_steam_running():
        return 1
    
    # Validate Steam path
    console.print(f"\n[cyan]Steam Installation:[/cyan] {steam_path}")
    
    if not validate_steam_directory(steam_path):
        console.print("[red]Error: Invalid Steam directory![/red]")
        return 1
    
    # Scan
    console.print("\n[bold]Scanning Steam installation...[/bold]")
    
    scanner = SteamScanner(steam_path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning...", total=None)
        try:
            scanner.scan()
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]Scan failed: {e}[/red]")
            return 1
    
    console.print("[green]✓ Scan complete[/green]")
    
    # Display results
    display_scan_results(scanner)
    
    # Check if any issues found
    if not scanner.has_issues():
        console.print("\n[green]🎉 No issues found! Your Steam installation is healthy.[/green]")
        return 0
    
    # Ask user what to do
    console.print("\n[bold]What would you like to do?[/bold]")
    console.print("1. Fix all issues automatically")
    console.print("2. Show detailed issue information")
    console.print("3. Dry run (show what would be fixed)")
    console.print("4. Exit without fixing")
    
    choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="1")
    
    if choice == "4":
        console.print("Exiting without making changes.")
        return 0
    
    if choice == "2":
        # Show detailed info
        for issue in scanner.issues:
            console.print(f"\n[cyan]{issue.game_name}[/cyan]")
            console.print(f"  Issue: {issue.description}")
            console.print(f"  Current Value: {issue.current_value}")
            console.print(f"  Expected Value: {issue.expected_value}")
            console.print(f"  Manifest: {issue.manifest_path}")
        return 0
    
    # Apply fixes
    dry_run = (choice == "3")
    backup_manager = BackupManager()
    fixer = SteamFixer(scanner, backup_manager, dry_run=dry_run)
    
    if not dry_run:
        if not Confirm.ask("\n[yellow]Apply fixes now?[/yellow]"):
            console.print("Cancelled.")
            return 0
    
    console.print()
    results = fixer.fix_all()
    
    # Show results
    console.print(f"\n[bold]Fix Results:[/bold]")
    console.print(f"  Fixed: [green]{results['fixed']}[/green]")
    console.print(f"  Failed: [red]{results['failed']}[/red]")
    
    if results['dry_run']:
        console.print("\n[yellow]This was a dry run. No changes were made.[/yellow]")
    else:
        console.print("\n[green]✓ Fixes applied successfully![/green]")
        console.print("You can now restart Steam.")
    
    return 0


@click.command()
@click.option('--steam-path', type=click.Path(exists=True, path_type=Path), 
              help='Path to Steam installation directory')
@click.option('--scan', is_flag=True, help='Scan only, do not fix')
@click.option('--fix-all', is_flag=True, help='Automatically fix all issues')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without making changes')
@click.option('--restore', type=str, help='Restore from backup (provide backup ID)')
@click.option('--list-backups', is_flag=True, help='List available backups')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(steam_path, scan, fix_all, dry_run, restore, list_backups, verbose):
    """
    Steam Library Fixer - Automatic Steam configuration repair tool.
    
    Fixes common issues like games downloading to wrong drives,
    orphaned downloads, and mismatched library configurations.
    """
    logger = get_logger(verbose=verbose)
    
    # List backups
    if list_backups:
        backup_manager = BackupManager()
        backups = backup_manager.list_backups()
        
        if not backups:
            console.print("No backups found.")
            return 0
        
        console.print("[bold]Available Backups:[/bold]\n")
        for backup in backups:
            console.print(f"  ID: [cyan]{backup.backup_id}[/cyan]")
            console.print(f"  Date: {backup.timestamp}")
            console.print(f"  Description: {backup.description}")
            console.print(f"  Files: {len(backup.files)}")
            console.print()
        return 0
    
    # Restore backup
    if restore:
        backup_manager = BackupManager()
        console.print(f"Restoring backup: {restore}")
        
        try:
            backup_manager.restore_backup(restore)
            console.print("[green]✓ Backup restored successfully![/green]")
            return 0
        except Exception as e:
            console.print(f"[red]Failed to restore backup: {e}[/red]")
            return 1
    
    # Get Steam path
    if not steam_path:
        steam_path = get_default_steam_path()
        if not steam_path:
            console.print("[red]Could not find Steam installation![/red]")
            console.print("Please specify path with --steam-path")
            return 1
    
    # Run in appropriate mode
    if scan or fix_all or dry_run:
        # Non-interactive mode
        if not check_steam_running():
            return 1
        
        scanner = SteamScanner(steam_path)
        console.print("Scanning Steam installation...")
        
        try:
            scanner.scan()
        except Exception as e:
            console.print(f"[red]Scan failed: {e}[/red]")
            return 1
        
        display_scan_results(scanner)
        
        if not scanner.has_issues():
            console.print("\n[green]No issues found![/green]")
            return 0
        
        if scan:
            return 0
        
        # Fix issues
        backup_manager = BackupManager()
        fixer = SteamFixer(scanner, backup_manager, dry_run=dry_run)
        results = fixer.fix_all()
        
        console.print(f"\nFixed: {results['fixed']}, Failed: {results['failed']}")
        return 0 if results['failed'] == 0 else 1
    else:
        # Interactive mode
        return interactive_mode(steam_path)


if __name__ == '__main__':
    sys.exit(main())
