import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from pathlib import Path
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def split_and_save_data(
    X: np.ndarray, 
    y: np.ndarray, 
    test_size: float = 0.2, 
    random_state: int = 42,
    output_dir: str = "data/processed"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform stratified train-test split and save datasets to CSV.
    
    Args:
        X (np.ndarray): Features.
        y (np.ndarray): Target.
        test_size (float): Proportion of the dataset to include in the test split.
        random_state (int): Random state for reproducibility.
        output_dir (str): Directory where the processed data will be saved.
        
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: X_train, X_test, y_train, y_test.
    """
    logger.info(f"Split data with test_size={test_size}, random_state={random_state}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Create directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save datasets
    # Note: Using numpy savetxt or pandas to save. Pandas is more flexible for csv.
    pd.DataFrame(X_train).to_csv(output_path / "X_train.csv", index=False)
    pd.DataFrame(X_test).to_csv(output_path / "X_test.csv", index=False)
    pd.Series(y_train).to_csv(output_path / "y_train.csv", index=False)
    pd.Series(y_test).to_csv(output_path / "y_test.csv", index=False)
    
    logger.info(f"Datasets saved successfully to {output_dir}")
    logger.info(f"X_train shape: {X_train.shape}, X_test shape: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test
