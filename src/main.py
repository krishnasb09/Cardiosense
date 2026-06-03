from pathlib import Path
from src.config.config_loader import load_config
from src.utils.logger import setup_logger
from src.data.data_loader import load_all_data
from src.data.preprocess import Preprocessor
from src.data.split import split_and_save_data

from src.models.model_factory import get_models
from src.models.train_models import train_all_models
from src.models.evaluate import evaluate_all_models
from src.models.model_selection import select_best_model
from src.features.feature_pipeline import run_feature_selection, apply_feature_mask
from src.explainability.shap_explainer import SHAPExplainer
from src.inference.prediction_pipeline import PredictionPipeline
import joblib

def main():
    """
    Main entry point for Stages 1, 2 & 3.
    Loads configuration, initializes logging, and runs full ML pipeline.
    """
    # Define paths
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "config.yaml"
    
    # Load configuration
    try:
        config = load_config(str(config_path))
    except Exception as e:
        print(f"Failed to load config: {e}")
        return

    # Initialize logger
    logger = setup_logger(
        name="CardioSense",
        log_file="experiments/experiment_logs/training.log",
        level="INFO"
    )

    logger.info("CardioSense initialized successfully")

    # --- Stage 2: Data Pipeline ---
    logger.info("Starting Stage 2: Data Pipeline")
    
    try:
        # 1. Load data
        df = load_all_data(str(project_root / "data" / "raw"))
        
        # 2. Preprocess data
        scaling_method = config.get("scaling_method", "standard")
        preprocessor = Preprocessor(scaling_method=scaling_method)
        X_processed, y = preprocessor.fit_transform(df)
        
        # Save preprocessor for inference
        preprocessor_dir = project_root / "models" / "preprocessors"
        preprocessor_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(preprocessor, preprocessor_dir / "preprocessor.joblib")
        logger.info(f"Fitted preprocessor saved to {preprocessor_dir}")
        
        # 3. Split and save data
        test_size = config.get("test_size", 0.2)
        random_state = config.get("random_state", 42)
        X_train, X_test, y_train, y_test = split_and_save_data(
            X_processed, 
            y, 
            test_size=test_size, 
            random_state=random_state,
            output_dir=str(project_root / "data" / "processed")
        )
        
        logger.info("Stage 2: Data Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}", exc_info=True)
        return

    # --- Stage 4: Feature Selection ---
    logger.info("Starting Stage 4: Feature Selection")
    
    try:
        method = config.get("feature_selection_method", "none")
        # For this example, let's assume if method is not 'none', we select top 10
        n_features = config.get("n_features_to_select", 10)
        
        # Get feature names from preprocessor
        feature_names = preprocessor.feature_names
        selected_features = feature_names.tolist() if feature_names is not None else None
        
        if feature_names is not None:
             beso_params = config.get("beso_params", {})
             selected_features = run_feature_selection(
                X_train, 
                y_train, 
                feature_names, 
                method=method, 
                n_features=n_features,
                report_dir=str(project_root / "reports" / "feature_reports"),
                **beso_params
            )
            
             # Apply selection
             X_train = apply_feature_mask(X_train, feature_names.tolist(), selected_features)
             X_test = apply_feature_mask(X_test, feature_names.tolist(), selected_features)
        else:
            logger.warning("Could not retrieve feature names from preprocessor. Skipping feature selection.")

        logger.info("Stage 4: Feature Selection completed successfully")
        
    except Exception as e:
        logger.error(f"Stage 4 failed: {e}", exc_info=True)
        return

    # --- Stage 3: Model Training & Evaluation ---
    logger.info("Starting Stage 3: Model Training & Evaluation")
    
    try:
        # 1. Get models
        models = get_models(random_state=random_state)
        
        # 2. Train models
        trained_models = train_all_models(
            models, 
            X_train, 
            y_train,
            output_dir=str(project_root / "models" / "trained_models")
        )
        
        # 3. Evaluate models
        all_metrics = evaluate_all_models(trained_models, X_test, y_test)
        
        # 4. Select best model
        primary_metric = config.get("primary_metric", "roc_auc")
        best_model_name = select_best_model(
            all_metrics, 
            primary_metric=primary_metric,
            output_dir=str(project_root / "models" / "model_metadata"),
            selected_features=selected_features
        )
        
        logger.info("Stage 3: Model Training & Evaluation completed successfully")
        
        # --- Stage 6: Explainability Module ---
        if best_model_name in trained_models:
            logger.info(f"Starting Stage 6: Explainability Module for {best_model_name}")
            
            # Use current feature names (selected ones)
            # If no selection occurred, selected_features is all feature_names
            explainer = SHAPExplainer(
                model=trained_models[best_model_name],
                X_test=X_test,
                feature_names=selected_features,
                report_dir=str(project_root / "reports" / "explainability_reports")
            )
            explainer.generate_report()
            logger.info("Stage 6: Explainability Module completed successfully")
        else:
            logger.warning("No best model found to explain.")

        # --- Stage 7: Prediction Pipeline Example ---
        logger.info("Starting Stage 7: Prediction Pipeline Demonstration")
        try:
            inference_pipeline = PredictionPipeline(config_path=str(config_path))
            
            # Use a sample from the original raw data as 'new' input for demo
            sample_data = df.head(5)
            logger.info(f"Running inference on {len(sample_data)} samples from raw data")
            
            # Predict
            results = inference_pipeline.predict(sample_data)
            logger.info(f"Inference Results:\n{results}")
            
            # Explain first sample
            inference_pipeline.explain(sample_data, index=0)
            
            logger.info("Stage 7: Prediction Pipeline Demonstration completed successfully")
            
        except Exception as e:
            logger.error(f"Stage 7 Demonstration failed: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Stage 3 failed: {e}", exc_info=True)
        return


if __name__ == "__main__":
    main()
