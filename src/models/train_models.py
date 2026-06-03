import logging
import numpy as np
from typing import Dict, Any
from pathlib import Path
from src.utils.save_load import save_model

logger = logging.getLogger(__name__)

def train_all_models(
    models: Dict[str, Any], 
    X_train: np.ndarray, 
    y_train: np.ndarray,
    output_dir: str = "models/trained_models"
) -> Dict[str, Any]:
    """
    Train a set of models.
    
    Args:
        models (Dict[str, Any]): Dictionary of model names and instances.
        X_train (np.ndarray): Training features.
        y_train (np.ndarray): Training target.
        output_dir (str): Directory to save trained models.
        
    Returns:
        Dict[str, Any]: Dictionary of model names and trained instances.
    """
    trained_models = {}
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for name, model in models.items():
        logger.info(f"Training model: {name}")
        try:
            model.fit(X_train, y_train.ravel())
            trained_models[name] = model
            
            # Save the model
            model_file = output_path / f"{name}.joblib"
            save_model(model, str(model_file))
            logger.info(f"Successfully trained and saved {name} to {model_file}")
            
        except Exception as e:
            logger.error(f"Failed to train {name}: {e}", exc_info=True)
            
    return trained_models
