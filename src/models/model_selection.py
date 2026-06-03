import logging
import json
from typing import Dict, Any
from pathlib import Path
from src.utils.save_load import save_json

logger = logging.getLogger(__name__)

def select_best_model(
    all_metrics: Dict[str, Dict[str, Any]], 
    primary_metric: str = "roc_auc",
    output_dir: str = "models/model_metadata",
    selected_features: list = None
) -> str:
    """
    Select the best model based on a primary metric and save metadata.
    
    Args:
        all_metrics (Dict[str, Dict[str, Any]]): Metrics for all models.
        primary_metric (str): The metric to use for selection.
        output_dir (str): Directory to save best model metadata.
        
    Returns:
        str: Name of the best model.
    """
    logger.info(f"Selecting best model based on {primary_metric}")
    
    best_model_name = None
    best_score = -float('inf')
    
    for name, metrics in all_metrics.items():
        score = metrics.get(primary_metric)
        if score is not None and score > best_score:
            best_score = score
            best_model_name = name
            
    if best_model_name:
        logger.info(f"Best model selected: {best_model_name} with {primary_metric}={best_score:.4f}")
        
        # Save metadata
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "best_model": best_model_name,
            "primary_metric": primary_metric,
            "score": best_score,
            "selected_features": selected_features,
            "all_metrics": all_metrics
        }
        
        save_json(metadata, str(output_path / "best_model.json"))
        logger.info(f"Best model metadata saved to {output_path / 'best_model.json'}")
        
    else:
        logger.warning("No model could be selected (all metrics are missing).")
        
    return best_model_name
