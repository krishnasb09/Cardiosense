import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from typing import List

logger = logging.getLogger(__name__)

def select_features_ensemble(
    X: np.ndarray, 
    y: np.ndarray, 
    feature_names: List[str],
    n_features_to_select: int = 10
) -> List[str]:
    """
    Select top features by averaging importance from RandomForest and XGBoost.
    
    Args:
        X (np.ndarray): Input features.
        y (np.ndarray): Target variable.
        feature_names (List[str]): List of all feature names.
        n_features_to_select (int): Number of features to select.
        
    Returns:
        List[str]: Names of the selected features.
    """
    logger.info(f"Starting Ensemble selection for top {n_features_to_select} features")
    
    # Train RandomForest to get importances
    rf = RandomForestClassifier(random_state=42)
    rf.fit(X, y.ravel())
    rf_importances = rf.feature_importances_
    
    # Train XGBoost to get importances
    xgb = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X, y.ravel())
    xgb_importances = xgb.feature_importances_
    
    # Average importances
    avg_importances = (rf_importances + xgb_importances) / 2
    
    # Create a Series for easy sorting
    importance_series = pd.Series(avg_importances, index=feature_names)
    selected_features = importance_series.nlargest(n_features_to_select).index.tolist()
    
    logger.info(f"Selected {len(selected_features)} features via Ensemble: {selected_features}")
    
    return selected_features
