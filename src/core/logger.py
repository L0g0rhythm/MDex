import logging
import logging.handlers
import sys
from pathlib import Path
from rich.logging import RichHandler

def setup_logger(name: str = "MDex", level: str = "INFO"):
    """Configures structured logging with Rich and rotating file output (Module 08/22)."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    root = logging.getLogger()
    if not root.handlers:
        # Module 08: Data Lifecycle - Rotating logs to prevent storage exhaustion
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "audit.log", 
            encoding="utf-8", 
            maxBytes=10*1024*1024, # 10MB
            backupCount=5
        )
        
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(rich_tracebacks=True),
                file_handler
            ]
        )
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

logger = setup_logger()
