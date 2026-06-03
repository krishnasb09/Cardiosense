import logging
import joblib
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from src.config.config_loader import load_config
from src.utils.logger import setup_logger
from src.utils.save_load import load_json

logger = logging.getLogger("CardioSense." + __name__)

class PredictionPipeline:
    """
    Pipeline for making predictions on new data using the best trained model.
    """

    def __init__(self, config_path: str):
        """
        Initialize the prediction pipeline.
        
        Args:
            config_path (str): Path to the configuration file.
        """
        self.project_root = Path(config_path).parent.parent
        self.config = load_config(config_path)
        
        # Paths
        self.model_dir = self.project_root / "models" / "trained_models"
        self.metadata_path = self.project_root / "models" / "model_metadata" / "best_model.json"
        self.preprocessor_path = self.project_root / "models" / "preprocessors" / "preprocessor.joblib"
        self.report_dir = self.project_root / "reports" / "explainability_reports"
        
        # Load components
        self.best_model_name = None
        self.selected_features = None
        self.model = None
        self.preprocessor = None
        
        self._load_components()

    def _load_components(self):
        """
        Load model, metadata, and preprocessor.
        """
        logger.info("Loading prediction pipeline components")
        
        try:
            # 1. Load metadata
            if self.metadata_path.exists():
                metadata = load_json(str(self.metadata_path))
                self.best_model_name = metadata.get("best_model")
                self.selected_features = metadata.get("selected_features")
                logger.info(f"Loaded metadata for best model: {self.best_model_name}")
            else:
                logger.error(f"Metadata not found at {self.metadata_path}")
                raise FileNotFoundError(f"Metadata not found at {self.metadata_path}")

            # 2. Load model
            model_file = self.model_dir / f"{self.best_model_name}.joblib"
            if model_file.exists():
                self.model = joblib.load(model_file)
                logger.info(f"Loaded trained model from {model_file}")
            else:
                logger.error(f"Model file not found at {model_file}")
                raise FileNotFoundError(f"Model file not found at {model_file}")

            # 3. Load preprocessor
            if self.preprocessor_path.exists():
                self.preprocessor = joblib.load(self.preprocessor_path)
                logger.info(f"Loaded preprocessor from {self.preprocessor_path}")
            else:
                logger.error(f"Preprocessor not found at {self.preprocessor_path}")
                raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")

        except Exception as e:
            logger.error(f"Failed to load PredictionPipeline components: {e}")
            raise

    def preprocess_input(self, X_new: pd.DataFrame) -> np.ndarray:
        """
        Preprocess new input data.
        
        Args:
            X_new (pd.DataFrame): New raw features.
            
        Returns:
            np.ndarray: Processed and selected features.
        """
        logger.info("Preprocessing new input data")
        
        # Apply the same transformations as during training
        # We need to handle the case where X_new might be missing the target column
        # Our preprocessor.transform expects a df WITH target_col to split it
        # Let's add a dummy target if it's missing just for the transform call
        if 'target' not in X_new.columns:
            temp_df = X_new.copy()
            temp_df['target'] = 0
            X_processed, _ = self.preprocessor.transform(temp_df)
        else:
            X_processed, _ = self.preprocessor.transform(X_new)

        # Apply feature mask (keep only selected features)
        if self.selected_features:
            all_feature_names = self.preprocessor.feature_names.tolist()
            feature_to_idx = {name: i for i, name in enumerate(all_feature_names)}
            selected_indices = [feature_to_idx[f] for f in self.selected_features if f in feature_to_idx]
            X_processed = X_processed[:, selected_indices]
            logger.info(f"Applied feature selection: kept {len(selected_indices)} features")

        return X_processed

    def predict(self, X_new: pd.DataFrame) -> pd.DataFrame:
        """
        Predict CAD for new patient data.
        
        Args:
            X_new (pd.DataFrame): New patient data.
            
        Returns:
            pd.DataFrame: Predictions and probabilities.
        """
        logger.info(f"Starting prediction for {len(X_new)} samples")
        
        X_processed = self.preprocess_input(X_new)
        
        # Predictions
        preds = self.model.predict(X_processed)
        
        # Probabilities
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_processed)[:, 1]
        else:
            probs = [None] * len(preds)
            
        result = pd.DataFrame({
            'prediction': preds,
            'probability': probs
        })
        
        logger.info(f"Predictions generated successfully")
        
        # Save if batch
        if len(X_new) > 1:
            save_path = self.project_root / "data" / "processed" / "predictions.csv"
            result.to_csv(save_path, index=False)
            logger.info(f"Batch predictions saved to {save_path}")
            
        return result

    def explain(self, X_new: pd.DataFrame, index: int = 0) -> None:
        """
        Generate SHAP explanation for a specific prediction.
        
        Args:
            X_new (pd.DataFrame): Input data.
            index (int): Index of the sample to explain.
        """
        logger.info(f"Generating SHAP explanation for sample at index {index}")
        
        X_processed = self.preprocess_input(X_new)
        X_sample = X_processed[index:index+1]
        
        try:
            # Use Explainer directly for simplicity in inference
            # We sample from training data if possible, or just use X_processed as background
            explainer = shap.Explainer(self.model, X_processed)
            shap_values = explainer(X_sample)
            
            # Extract pos class values if needed
            if len(shap_values.values.shape) == 3:
                # Shape (samples, features, classes)
                shap_values = shap_values[:, :, 1]

            # Generate and save waterfall plot
            plt.figure(figsize=(10, 6))
            shap.plots.waterfall(shap_values[0], show=False)
            plt.tight_layout()
            
            plot_path = self.report_dir / f"prediction_explanation_sample_{index}.png"
            plt.savefig(plot_path)
            plt.close()
            
            # Log top impacts
            vals = shap_values.values[0]
            top_indices = np.argsort(np.abs(vals))[::-1][:3]
            logger.info(f"Top 3 Feature Impacts for sample {index}:")
            for idx in top_indices:
                logger.info(f"  - {self.selected_features[idx]}: {vals[idx]:.4f}")
                
            logger.info(f"Explanation saved to {plot_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
