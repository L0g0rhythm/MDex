from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()

def display_welcome():
    console.print(Panel.fit(
        "[bold cyan]MDex Omni-v5[/bold cyan]\n[italic]The Singularity of Manga Downloading[/italic]",
        border_style="magenta"
    ))

def display_error(message: str):
    console.print(f"[bold red]❌ ERRO:[/bold red] {message}")

def display_success(message: str):
    console.print(f"[bold green]✅ SUCESSO:[/bold green] {message}")

def create_progress_bar():
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
