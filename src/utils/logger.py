import sys
import os
import logging
from pathlib import Path

try:
    from loguru import logger as loguru_logger
    HAS_LOGURU = True
except ImportError:
    HAS_LOGURU = False

def setup_logger(log_dir: str = "./logs", log_level: str = "INFO"):
    """Configures structured logger with console formatting and file output."""
    os.makedirs(log_dir, exist_ok=True)
    
    if HAS_LOGURU:
        loguru_logger.remove()
        loguru_logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level
        )
        log_file_path = Path(log_dir) / "vera_system.log"
        loguru_logger.add(
            str(log_file_path),
            rotation="10 MB",
            retention="14 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
            level=log_level,
            encoding="utf-8"
        )
        return loguru_logger
    else:
        # Standard library logging fallback
        std_logger = logging.getLogger("VERA")
        std_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        if not std_logger.handlers:
            # Console handler
            c_handler = logging.StreamHandler(sys.stdout)
            c_format = logging.Formatter("[%(asctime)s] %(levelname)-8s %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            c_handler.setFormatter(c_format)
            std_logger.addHandler(c_handler)
            
            # File handler
            f_handler = logging.FileHandler(os.path.join(log_dir, "vera_system.log"), encoding="utf-8")
            f_format = logging.Formatter("[%(asctime)s] %(levelname)-8s %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            f_handler.setFormatter(f_format)
            std_logger.addHandler(f_handler)
            
        # Add helper methods if missing to mirror loguru
        if not hasattr(std_logger, "success"):
            std_logger.success = std_logger.info
            
        return std_logger

# Initialize default logger
logger = setup_logger()
