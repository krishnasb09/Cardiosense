from typing import Dict, Any, Union, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


def calculate_classification_metrics(
    y_true: Union[np.ndarray, list],
    y_pred: Union[np.ndarray, list],
    y_prob: Optional[Union[np.ndarray, list]] = None,
) -> Dict[str, Any]:
    """
    Calculate common classification metrics.

    Args:
        y_true (Union[np.ndarray, list]): Ground truth labels.
        y_pred (Union[np.ndarray, list]): Predicted labels.
        y_prob (Optional[Union[np.ndarray, list]]): Predicted probabilities for the positive class.

    Returns:
        Dict[str, Any]: A dictionary containing accuracy, precision, recall, f1, 
                        roc_auc (if y_prob provided), confusion_matrix, and 
                        classification_report (string).
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, zero_division=0),
    }

    if y_prob is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
        except Exception:
            metrics["roc_auc"] = None

    return metrics
