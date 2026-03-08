from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from src.core.config import THEME_COLOR, ERROR_COLOR, SUCCESS_COLOR

console = Console()

def display_welcome():
    console.print(Panel.fit(
        "[bold cyan]MDex Singularity v4.0[/bold cyan]\n[italic]L0g0rhythm Authority Core - 2026 Edition[/italic]",
        border_style=THEME_COLOR
    ))

def display_error(message: str):
    console.print(f"[{ERROR_COLOR}]ERROR:[/{ERROR_COLOR}] {message}")

def display_success(message: str):
    console.print(f"[{SUCCESS_COLOR}]SUCCESS:[/{SUCCESS_COLOR}] {message}")

def create_progress_bar():
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, pulse_style="cyan"),
        TaskProgressColumn(),
        console=console
    )
