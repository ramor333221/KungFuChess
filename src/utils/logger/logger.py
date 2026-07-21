import logging
from pathlib import Path


def setup_logger(name: str, log_file: str) -> logging.Logger:
    """Sets up a file-based logger inside the 'logsFile' directory."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_path = Path("logsFile") / log_file

        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(filename=str(log_path), encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger