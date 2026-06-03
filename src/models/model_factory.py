import logging
from typing import Dict, Any, List
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

def get_models(model_names: List[str] = None, random_state: int = 42) -> Dict[str, Any]:
    """
    Returns a dictionary of model instances.
    """
    logger.info(f"Initializing models with random_state={random_state}")
    
    all_models = {
        "logistic_regression": LogisticRegression(
            random_state=random_state, 
            max_iter=1000
        ),
        "random_forest": RandomForestClassifier(
            random_state=random_state
        ),
        "xgboost": XGBClassifier(
            random_state=random_state,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    }
    
    if model_names:
        return {name: all_models[name] for name in model_names if name in all_models}
    
    return all_models
