import logging
import sys
from pathlib import Path
from typing import Optional


class CardioLogger:
    """
    Custom logging utility for the CardioSense project.
    Provides logging to both console and a specified log file.
    """

    def __init__(
        self,
        name: str = "CardioSense",
        log_file: str = "experiments/experiment_logs/training.log",
        level: int = logging.INFO,
    ):
        """
        Initialize the logger.

        Args:
            name (str): Name of the logger.
            log_file (str): Path to the log file.
            level (int): Logging level (logging.INFO, logging.DEBUG, etc.).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid adding handlers multiple times if the logger is already initialized
        if not self.logger.handlers:
            self._setup_handlers(log_file)

    def _setup_handlers(self, log_file: str) -> None:
        """
        Set up console and file handlers.

        Args:
            log_file (str): Path to the log file.
        """
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """
        Return the configured logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger


def setup_logger(
    name: str = "CardioSense",
    log_file: str = "experiments/experiment_logs/training.log",
    level: str = "INFO",
) -> logging.Logger:
    """
    Convenience function to set up and return a logger.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    cardio_logger = CardioLogger(name=name, log_file=log_file, level=numeric_level)
    return cardio_logger.get_logger()

def get_logger(name: str) -> logging.Logger:
    """
    Returns an existing logger or sets up a new one with defaults.
    """
    return logging.getLogger("CardioSense." + name)
