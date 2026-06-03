import logging
import numpy as np
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from typing import List, Tuple

logger = logging.getLogger(__name__)

def select_features_rfe(
    X: np.ndarray, 
    y: np.ndarray, 
    feature_names: List[str],
    n_features_to_select: int = 10
) -> List[str]:
    """
    Select top features using Recursive Feature Elimination with Logistic Regression.
    
    Args:
        X (np.ndarray): Input features.
        y (np.ndarray): Target variable.
        feature_names (List[str]): List of all feature names.
        n_features_to_select (int): Number of features to select.
        
    Returns:
        List[str]: Names of the selected features.
    """
    logger.info(f"Starting RFE selection for top {n_features_to_select} features")
    
    # Use LogisticRegression as base estimator
    estimator = LogisticRegression(max_iter=1000, random_state=42)
    
    # Initialize RFE
    selector = RFE(estimator, n_features_to_select=n_features_to_select, step=1)
    
    # Fit selector
    selector = selector.fit(X, y.ravel())
    
    # Get selected feature names
    selected_indices = selector.support_
    selected_features = [feature_names[i] for i, selected in enumerate(selected_indices) if selected]
    
    logger.info(f"Selected {len(selected_features)} features via RFE: {selected_features}")
    
    return selected_features
