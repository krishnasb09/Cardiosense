import logging
import yaml
import pandas as pd
import joblib
import sys
from pathlib import Path

# Add project root to sys.path for direct execution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from typing import Dict, Any, List, Optional

from src.config.config_loader import load_config
from src.utils.logger import get_logger, setup_logger
from src.data.data_loader import load_all_data
from src.data.preprocess import Preprocessor
from src.data.split import split_and_save_data
from src.features.feature_pipeline import run_feature_selection
from src.models.model_factory import get_models
from src.models.train_models import train_all_models
from src.models.evaluate import evaluate_all_models
from src.models.model_selection import select_best_model
from src.explainability.shap_explainer import SHAPExplainer

class TrainingPipeline:
    """
    Unified training pipeline for CardioSense.
    """

    def __init__(self, config_path: str):
        """
        Initialize the training pipeline.
        """
        self.config_path = config_path
        self.config = load_config(config_path)
        
        # Setup Logger
        self.logger = setup_logger(
            name="TrainingPipeline",
            log_file="experiments/experiment_logs/training.log",
            level="INFO"
        )
        
        self.paths = self.config.get("paths", {})
        # Project root is three levels up from src/pipeline/training_pipeline.py
        self.project_root = Path(__file__).resolve().parent.parent.parent
        
    def run(self):
        """
        Execute the full training pipeline.
        """
        self.logger.info("Starting CardioSense Training Pipeline")
        
        try:
            # 1. Load Data
            raw_data_path = str(self.project_root / self.paths.get("raw_data", "data/raw/"))
            df = load_all_data(raw_data_path)
            self.logger.info(f"Loaded {len(df)} samples from {raw_data_path}")

            # 2. Preprocess Data
            scaling_method = self.config.get("scaling_method", "standard")
            preprocessor = Preprocessor(scaling_method=scaling_method)
            X_processed, y = preprocessor.fit_transform(df)
            
            # Save Preprocessing Objects (scaler and encoder are inside preprocessor.preprocessor)
            # The User's prediction_pipeline expects separate pkl files for scaler and encoder
            # However, our Preprocessor class wraps them in a ColumnTransformer.
            # I will save the whole preprocessor but also extract sub-components if needed for user compatibility.
            
            preprocessor_save_path = self.project_root / "models" / "preprocessors" / "preprocessor.joblib"
            preprocessor_save_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(preprocessor, preprocessor_save_path)
            
            # For user's PredictionPipeline compatibility:
            # Note: In our current Preprocessor, we use a ColumnTransformer with Pipelines.
            # Creating separate scaler.pkl and encoder.pkl for the whole thing might be tricky
            # but I'll save them to the paths specified in config.
            
            scaler_path = self.project_root / self.config["preprocessing"]["scaler_path"]
            scaler_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(preprocessor.preprocessor, scaler_path) 
            
            encoder_path = self.project_root / self.config["preprocessing"]["encoder_path"]
            encoder_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(preprocessor.preprocessor, encoder_path) # Symmetric for now
            
            # 3. Split Data
            test_size = self.config.get("test_size", 0.2)
            random_state = self.config.get("random_state", 42)
            X_train, X_test, y_train, y_test = split_and_save_data(X_processed, y, test_size, random_state)
            
            # 4. Feature Selection
            method = self.config.get("feature_selection_method", "none")
            feature_names = preprocessor.feature_names
            
            selected_features = feature_names.tolist()
            if method != "none":
                self.logger.info(f"Running feature selection with method: {method}")
                beso_params = self.config.get("beso_params", {})
                
                # run_feature_selection returns only the list of feature names
                selected_features = run_feature_selection(
                    X_train=X_train,
                    y_train=y_train,
                    feature_names=feature_names,
                    method=method,
                    **beso_params
                )
                
                # Apply mask to both train and test sets
                from src.features.feature_pipeline import apply_feature_mask
                X_train = apply_feature_mask(X_train, feature_names, selected_features)
                X_test = apply_feature_mask(X_test, feature_names, selected_features)
                self.logger.info(f"Features filtered. New shape: {X_train.shape}")
            
            # 5. Model Training
            models_to_train = self.config.get("models", ["logistic_regression", "random_forest"])
            models = get_models(models_to_train, random_state=random_state)
            trained_models = train_all_models(models, X_train, y_train)
            
            # 6. Evaluation
            eval_output_dir = str(self.project_root / "reports" / "evaluation_reports")
            all_metrics = evaluate_all_models(trained_models, X_test, y_test, output_dir=eval_output_dir)
            
            # 7. Model Selection
            best_model_name = select_best_model(
                all_metrics, 
                primary_metric=self.config.get("primary_metric", "roc_auc"),
                output_dir=str(self.project_root / self.paths.get("model_metadata", "models/model_metadata")),
                selected_features=selected_features
            )
            
            # Save the best model as 'best_model.pkl' for PredictionPipeline compatibility
            if best_model_name:
                best_model = trained_models[best_model_name]
                best_model_path = self.project_root / self.paths.get("trained_models", "models/trained_models") / "best_model.pkl"
                joblib.dump(best_model, best_model_path)
                self.logger.info(f"Saved best model {best_model_name} to {best_model_path}")
            
            # 8. Explainability
            if best_model_name:
                self.logger.info(f"Generating SHAP report for best model: {best_model_name}")
                explainer = SHAPExplainer(
                    model=trained_models[best_model_name],
                    X_test=X_test,
                    feature_names=selected_features,
                    report_dir=str(self.project_root / self.paths.get("explainability_reports", "reports/explainability_reports"))
                )
                explainer.generate_report()

            self.logger.info("Training pipeline completed successfully")
            
        except Exception as e:
            self.logger.error(f"Training pipeline failed: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    pipeline = TrainingPipeline(config_path="src/config/config.yaml")
    pipeline.run()
