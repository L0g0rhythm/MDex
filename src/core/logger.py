import logging
import sys
from pathlib import Path
from rich.logging import RichHandler

def setup_logger(name: str = "MDex"):
    """Configures structured logging with Rich and file output."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(rich_tracebacks=True),
            logging.FileHandler(log_dir / "audit.log", encoding="utf-8")
        ]
    )

    return logging.getLogger(name)

logger = setup_logger()
