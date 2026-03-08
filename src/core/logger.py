import logging
import sys
from pathlib import Path
from rich.logging import RichHandler

def setup_logger(name: str = "MDex", level: str = "INFO"):
    """Configures structured logging with Rich and file output."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Note: basicConfig only configures the root logger the first time it is called.
    # For sub-loggers, we should set the level explicitly.
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(rich_tracebacks=True),
                logging.FileHandler(log_dir / "audit.log", encoding="utf-8")
            ]
        )
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

logger = setup_logger()
