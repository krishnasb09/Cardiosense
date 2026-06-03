import os
import yaml
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def load_config(path: str) -> Dict[str, Any]:
    """
    Safely load a YAML configuration file.

    Args:
        path (str): Path to the YAML file.

    Returns:
        Dict[str, Any]: Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
        ValueError: If the file is not a valid YAML or does not contain a dictionary.
        RuntimeError: For other unexpected errors during file access.
    """
    if not os.path.exists(path):
        error_msg = f"Configuration file not found at: {path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            logger.warning(f"Configuration file {path} is empty.")
            return {}

        if not isinstance(config, dict):
            error_msg = f"Configuration at {path} must be a YAML dictionary."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Configuration loaded successfully from {path}")
        return config

    except yaml.YAMLError as exc:
        error_msg = f"Failed to parse YAML file at {path}: {exc}"
        logger.error(error_msg)
        raise ValueError(error_msg) from exc
    except Exception as exc:
        error_msg = f"An unexpected error occurred while loading config from {path}: {exc}"
        logger.critical(error_msg)
        raise RuntimeError(error_msg) from exc
