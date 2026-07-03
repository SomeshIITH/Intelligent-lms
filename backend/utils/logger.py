import sys
from pathlib import Path
from loguru import logger
from config import settings


def setup_logger() -> None:
    """
    Configures Loguru global logging pipelines.
    Establishes thread-safe console output and rolling file logging
    configured specifically to remain robust against duplicate uvicorn handlers.
    """
    # Remove default standard logger handlers to eliminate output duplication
    logger.remove()

    # Define common format strings containing granular processing context
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 1. Console Logging Stream Handler
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=log_format,
        colorize=True,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
    )

    # Construct and resolve logging directory safely across operating systems
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "intelligent_lms.log"

    # 2. File Logging Rolling Stream Handler
    logger.add(
        str(log_file_path),
        level=settings.LOG_LEVEL,
        format=log_format,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        enqueue=True,  # Guarantees thread-safe asynchronous queue logging
        backtrace=True,
        diagnose=True,
    )

    logger.info(
        f"[LOGGER SETUP] Initialized extensive log subsystem. "
        f"Console Level: {settings.LOG_LEVEL} | File Path: {log_file_path}"
    )


# Execute configuration immediately upon module initialization
setup_logger()