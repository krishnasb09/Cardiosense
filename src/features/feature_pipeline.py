import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional
from src.features.rfe_selection import select_features_rfe
from src.features.ensemble_selection import select_features_ensemble
from src.features.beso_selection import select_features_beso
from src.utils.save_load import save_json

logger = logging.getLogger(__name__)

def run_feature_selection(
    X_train: np.ndarray, 
    y_train: np.ndarray, 
    feature_names: List[str],
    method: str = "none",
    n_features: int = 10,
    report_dir: str = "reports/feature_reports",
    **kwargs
) -> List[str]:
    """
    Run the selected feature selection method.
    
    Args:
        X_train (np.ndarray): Training features.
        y_train (np.ndarray): Training target.
        feature_names (List[str]): All feature names.
        method (str): Selection method ('none', 'rfe', 'ensemble').
        n_features (int): Number of features to select.
        report_dir (str): Directory to save feature reports.
        
    Returns:
        List[str]: Selected feature names.
    """
    logger.info(f"Running feature selection with method: {method}")
    
    if method == "none":
        selected_features = feature_names.tolist() if isinstance(feature_names, np.ndarray) else list(feature_names)
        logger.info("No feature selection applied. Using all features.")
    elif method == "rfe":
        selected_features = select_features_rfe(X_train, y_train, feature_names, n_features)
    elif method == "ensemble":
        selected_features = select_features_ensemble(X_train, y_train, feature_names, n_features)
    elif method == "beso":
        # Pass population_size and max_iterations if present in kwargs
        pop_size = kwargs.get("population_size", 20)
        max_iter = kwargs.get("max_iterations", 50)
        selected_features = select_features_beso(X_train, y_train, feature_names, pop_size=pop_size, max_iter=max_iter)
    else:
        logger.warning(f"Unknown feature selection method: {method}. Defaulting to all features.")
        selected_features = feature_names.tolist() if isinstance(feature_names, np.ndarray) else list(feature_names)

    # Save report
    report_path = Path(report_dir)
    report_path.mkdir(parents=True, exist_ok=True)
    
    report_data = {
        "method": method,
        "n_features_selected": len(selected_features),
        "selected_features": selected_features,
        "total_features_before": len(feature_names)
    }
    
    save_json(report_data, str(report_path / "selected_features.json"))
    logger.info(f"Feature selection report saved to {report_path / 'selected_features.json'}")
    
    return selected_features

def apply_feature_mask(X: np.ndarray, feature_names: List[str], selected_features: List[str]) -> np.ndarray:
    """
    Filter the feature matrix to include only selected features.
    
    Args:
        X (np.ndarray): Original feature matrix.
        feature_names (List[str]): Original list of feature names.
        selected_features (List[str]): List of features to keep.
        
    Returns:
        np.ndarray: Filtered feature matrix.
    """
    # Create a mapping of feature names to indices
    feature_to_idx = {name: i for i, name in enumerate(feature_names)}
    
    # Get indices of selected features
    selected_indices = [feature_to_idx[f] for f in selected_features if f in feature_to_idx]
    
    return X[:, selected_indices]
