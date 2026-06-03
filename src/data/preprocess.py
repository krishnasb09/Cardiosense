import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Preprocessor:
    """
    Preprocessor class to handle missing values, encoding, and scaling for CardioSense.
    """

    def __init__(self, scaling_method: str = "standard", scaler: Any = None, encoder: Any = None):
        """
        Initialize the Preprocessor.
        
        Args:
            scaling_method (str): Method for scaling ('standard' or 'minmax').
            scaler: Optional pre-fitted scaler.
            encoder: Optional pre-fitted encoder.
        """
        self.scaling_method = scaling_method
        self.scaler = scaler
        self.encoder = encoder
        self.preprocessor = None
        self.feature_names = None
        
        # If we have a fitted scaler (ColumnTransformer), extract feature names
        if self.scaler and hasattr(self.scaler, "get_feature_names_out"):
            try:
                self.feature_names = self.scaler.get_feature_names_out()
            except Exception:
                pass

    def fit_transform(self, df: pd.DataFrame, target_col: str = "target") -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit the preprocessor on the data and transform it.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            target_col (str): Name of the target column.
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Processed features (X) and target (y).
        """
        logger.info("Starting fit_transform")
        
        X = df.drop(columns=[target_col])
        y = df[target_col].values
        
        # Identify numeric and categorical columns
        numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()
        
        logger.info(f"Numeric features: {numeric_features}")
        logger.info(f"Categorical features: {categorical_features}")
        
        # Define transformers
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler() if self.scaling_method == "standard" else MinMaxScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        # Combine transformers
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
            
        X_processed = self.preprocessor.fit_transform(X)
        
        # Extract feature names if possible (useful for analysis later)
        try:
            # For newer versions of scikit-learn
            self.feature_names = self.preprocessor.get_feature_names_out()
        except Exception:
            self.feature_names = None
            
        logger.info(f"Preprocessing completed. Feature dimension: {X_processed.shape}")
        
        return X_processed, y

    def transform(self, df: pd.DataFrame, target_col: Optional[str] = "target") -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Transform the data using the fitted preprocessor.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            target_col (str): Name of the target column (optional).
            
        Returns:
            Tuple[np.ndarray, Optional[np.ndarray]]: Processed features (X) and target (y).
        """
        if self.preprocessor is None and (self.scaler is None or self.encoder is None):
            logger.error("Preprocessor has not been fitted and no external scaler/encoder provided.")
            raise ValueError("Preprocessor not ready.")
            
        if target_col and target_col in df.columns:
            X = df.drop(columns=[target_col])
            y = df[target_col].values
        else:
            X = df
            y = None
            
        if self.preprocessor:
            X_processed = self.preprocessor.transform(X)
        elif self.scaler:
            # The scaler attribute might hold the whole ColumnTransformer
            X_processed = self.scaler.transform(X)
        else:
            logger.error("No valid preprocessor or scaler found for transformation.")
            raise ValueError("Preprocessor not ready.")

        return X_processed, y
