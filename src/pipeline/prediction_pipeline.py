from pathlib import Path
import pandas as pd
import joblib
import yaml
import numpy as np
import matplotlib.pyplot as plt
from src.utils.logger import get_logger
from src.utils.save_load import load_json
from src.data.preprocess import Preprocessor


def _load_shap():
    try:
        import shap

        return shap
    except OSError as exc:
        raise RuntimeError(
            "SHAP could not be loaded because one of its optional dependencies "
            "failed to initialize. Predictions will still work, but SHAP "
            "explanations are unavailable in this environment."
        ) from exc

class PredictionPipeline:
    def __init__(self, config_path: str):
        # -----------------------------
        # Load config
        # -----------------------------
        # -----------------------------
        # Load config
        # -----------------------------
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Calculate project root from config path (assuming src/config/config.yaml)
        self.project_root = Path(config_path).resolve().parent.parent.parent

        # -----------------------------
        # Initialize logger
        # -----------------------------
        self.logger = get_logger("PredictionPipeline")

        # -----------------------------
        # Load best trained model
        # -----------------------------
        # Resolve path relative to project root
        model_rel_path = self.config["paths"]["trained_models"]
        model_path = self.project_root / model_rel_path / "best_model.pkl"
        
        self.model = joblib.load(model_path)
        self.logger.info(f"Loaded model from {model_path}")

        # -----------------------------
        # Load preprocessing objects
        # -----------------------------
        scaler_rel_path = self.config["preprocessing"]["scaler_path"]
        encoder_rel_path = self.config["preprocessing"]["encoder_path"]
        
        scaler_path = self.project_root / scaler_rel_path
        encoder_path = self.project_root / encoder_rel_path
        
        self.scaler = joblib.load(scaler_path)
        self.encoder = joblib.load(encoder_path)
        self.preprocessor = Preprocessor(scaler=self.scaler, encoder=self.encoder)

        # -----------------------------
        # Load selected features
        # -----------------------------
        features_rel_path = self.config["feature_selection"]["selected_features_path"]
        features_path = self.project_root / features_rel_path
        
        # Handle case where features might be a list or a dict with "selected_features"
        features_data = load_json(str(features_path))
        if isinstance(features_data, dict):
            self.selected_features = features_data.get("selected_features", [])
        else:
            self.selected_features = features_data
            
        self.logger.info(f"Loaded selected features: {self.selected_features}")

    def preprocess_input(self, X_new: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess new patient data
        """
        # Apply preprocessing (scaling + encoding)
        X_processed, _ = self.preprocessor.transform(X_new, target_col=None)
        
        feature_names = self.preprocessor.feature_names
        
        # Keep only selected features
        # X_processed is a numpy array, we need to handle indexing
        # The Preprocessor class should ideally return a DF or we need the feature map
        # Based on my Preprocessor, X_processed is a numpy array.
        # But user's code treats it like a DF: X_processed[self.selected_features]
        # I'll convert it back to DF if possible
        
        X_df = pd.DataFrame(X_processed, columns=feature_names)
        
        X_final = X_df[self.selected_features]
        self.logger.info(f"Preprocessed input shape: {X_final.shape}")
        return X_final

    def predict(self, X_new: pd.DataFrame) -> pd.DataFrame:
        """
        Predict CAD class (0/1) and probability
        """
        X_proc = self.preprocess_input(X_new)
        preds = self.model.predict(X_proc)
        
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_proc)[:, 1]
        else:
            probs = [None] * len(preds)

        result = pd.DataFrame({
            "prediction": preds,
            "probability": probs
        })
        self.logger.info(f"Prediction completed for {len(X_new)} patient(s)")
        return result

    def get_feature_importance(self, X_new: pd.DataFrame) -> list:
        """
        Calculate SHAP values for a given input and return as a list of dicts.
        """
        X_proc = self.preprocess_input(X_new)
        shap = _load_shap()
        
        # Determine SHAP explainer type
        model_type = type(self.model).__name__.lower()
        if "forest" in model_type or "xgb" in model_type or "gradient" in model_type:
            explainer = shap.TreeExplainer(self.model)
        else:
            explainer = shap.KernelExplainer(self.model.predict_proba, X_proc)

        shap_values = explainer.shap_values(X_proc)

        # Handle potential list/multi-dimensional output for binary classification
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]
        elif len(shap_values.shape) == 3:
            shap_values = shap_values[:, :, 1]
            
        # Get importance for the first row (assuming single patient)
        patient_shap = shap_values[0]
        
        # Format for frontend
        formatted_shap = []
        for i, val in enumerate(patient_shap):
            feature_name = self.selected_features[i]
            # Clean up feature names for display
            clean_name = feature_name.replace("num__", "").replace("_", " ").title()
            formatted_shap.append({
                "feature": clean_name,
                "importance": float(round(val, 4))
            })
            
        # Sort by absolute importance
        formatted_shap.sort(key=lambda x: abs(x["importance"]), reverse=True)
        return formatted_shap[:10] # Top 10

    def get_model_feature_importance(self) -> list:
        """
        Return model-native feature importance when SHAP is unavailable.
        """
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
        elif hasattr(self.model, "coef_"):
            importances = np.ravel(self.model.coef_)
        else:
            return []

        formatted_importance = []
        for feature_name, value in zip(self.selected_features, importances):
            clean_name = feature_name.replace("num__", "").replace("_", " ").title()
            formatted_importance.append({
                "feature": clean_name,
                "importance": float(round(value, 4))
            })

        formatted_importance.sort(key=lambda x: abs(x["importance"]), reverse=True)
        return formatted_importance[:10]

    def explain(self, X_new: pd.DataFrame):
        """
        Generate SHAP explanations for new input
        """
        X_proc = self.preprocess_input(X_new)
        shap = _load_shap()

        # Determine SHAP explainer type
        model_type = type(self.model).__name__.lower()
        if "forest" in model_type or "xgb" in model_type or "gradient" in model_type:
            explainer = shap.TreeExplainer(self.model)
        else:
            explainer = shap.KernelExplainer(self.model.predict_proba, X_proc)

        shap_values = explainer.shap_values(X_proc)

        # Save SHAP plots
        shap_dir = Path(self.config["paths"]["explainability_reports"])
        shap_dir.mkdir(parents=True, exist_ok=True)

        for i in range(X_proc.shape[0]):
            # Handle potential list output for multiclass/binary
            base_value = explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)) and len(base_value) == 2:
                base_value = base_value[1]
                
            current_shap_values = shap_values
            if isinstance(current_shap_values, list) and len(current_shap_values) == 2:
                current_shap_values = current_shap_values[1]
                
            # If shape (samples, features, classes)
            if len(current_shap_values.shape) == 3:
                current_shap_values = current_shap_values[:, :, 1]

            shap.force_plot(
                base_value,
                current_shap_values[i],
                X_proc.iloc[i],
                matplotlib=True,
                show=False
            )
            plot_path = shap_dir / f"shap_patient_{i+1}.png"
            plt.savefig(plot_path)
            plt.close()
            self.logger.info(f"SHAP plot saved: {plot_path}")

        self.logger.info("SHAP explanation completed")
