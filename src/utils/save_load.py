import json
import joblib
from pathlib import Path
from typing import Any, Union


def save_model(model: Any, path: Union[str, Path]) -> None:
    """
    Save a model to a file using joblib.

    Args:
        model (Any): The model to save.
        path (Union[str, Path]): Path where the model will be saved.
    """
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, save_path)


def load_model(path: Union[str, Path]) -> Any:
    """
    Load a model from a file using joblib.

    Args:
        path (Union[str, Path]): Path to the model file.

    Returns:
        Any: The loaded model.
    """
    load_path = Path(path)
    if not load_path.exists():
        raise FileNotFoundError(f"Model file not found at: {load_path}")
    return joblib.load(load_path)


def save_json(data: Any, path: Union[str, Path], indent: int = 4) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Any): Data to save.
        path (Union[str, Path]): Path where the JSON file will be saved.
        indent (int): Indentation level for JSON formatting.
    """
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def load_json(path: Union[str, Path]) -> Any:
    """
    Load data from a JSON file.

    Args:
        path (Union[str, Path]): Path to the JSON file.

    Returns:
        Any: The loaded data.
    """
    load_path = Path(path)
    if not load_path.exists():
        raise FileNotFoundError(f"JSON file not found at: {load_path}")
    with open(load_path, "r", encoding="utf-8") as f:
        return json.load(f)
