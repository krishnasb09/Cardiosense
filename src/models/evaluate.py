import logging
import numpy as np
from typing import Dict, Any
from src.utils.metrics import calculate_classification_metrics

logger = logging.getLogger(__name__)

from src.utils.save_load import save_json
from pathlib import Path

def evaluate_all_models(
    models: Dict[str, Any], 
    X_test: np.ndarray, 
    y_test: np.ndarray,
    output_dir: str = None
) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate trained models and return metrics.
    
    Args:
        models (Dict[str, Any]): Dictionary of model names and trained instances.
        X_test (np.ndarray): Test features.
        y_test (np.ndarray): Test target.
        
    Returns:
        Dict[str, Dict[str, Any]]: Metrics for each model.
    """
    all_metrics = {}
    
    for name, model in models.items():
        logger.info(f"Evaluating model: {name}")
        try:
            # Predict labels
            y_pred = model.predict(X_test)
            
            # Predict probabilities if supported
            y_prob = None
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
                
            # Calculate metrics
            metrics = calculate_classification_metrics(y_test, y_pred, y_prob)
            all_metrics[name] = metrics
            
            # Log summary
            logger.info(f"Metrics for {name}: Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}")
            
        except Exception as e:
            logger.error(f"Failed to evaluate {name}: {e}", exc_info=True)
            
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        save_json(all_metrics, str(out_path / "evaluation_metrics.json"))
        logger.info(f"Evaluation metrics saved to {out_path / 'evaluation_metrics.json'}")
            
    return all_metrics
