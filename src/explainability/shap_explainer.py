import logging
import shap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CardioSense." + __name__)

class SHAPExplainer:
    """
    Explainability class for CardioSense using SHAP.
    """

    def __init__(
        self, 
        model: Any, 
        X_test: np.ndarray, 
        feature_names: List[str],
        report_dir: str = "reports/explainability_reports"
    ):
        self.model = model
        self.X_test = X_test
        self.feature_names = feature_names
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.explainer = None
        self.shap_values = None

    def generate_report(self) -> None:
        """
        Produce a full SHAP explainability report.
        """
        logger.info("Initializing SHAP Explainer")
        
        # Detect model type and select explainer
        # Some tree models have specific explainers for speed
        tree_models = (
            "RandomForestClassifier", 
            "XGBClassifier", 
            "GradientBoostingClassifier",
            "ExtraTreesClassifier"
        )
        model_name = type(self.model).__name__
        
        try:
            if model_name in tree_models:
                logger.info(f"Using TreeExplainer for {model_name}")
                self.explainer = shap.TreeExplainer(self.model)
            elif "LogisticRegression" in model_name or "SVC" in model_name:
                logger.info(f"Using KernelExplainer (approx) for {model_name}")
                # KernelExplainer can be slow, use a small background set if needed
                # Here we use the test set directly as an approximation
                self.explainer = shap.KernelExplainer(self.model.predict_proba, shap.sample(self.X_test, 10))
            else:
                logger.info(f"Defaulting to Explainer for {model_name}")
                self.explainer = shap.Explainer(self.model, self.X_test)

            logger.info("Computing SHAP values (this may take a moment)")
            self.shap_values = self.explainer.shap_values(self.X_test)
            
            # Debug shape
            if isinstance(self.shap_values, list):
                logger.debug(f"SHAP values is a list of length {len(self.shap_values)}")
                for i, v in enumerate(self.shap_values):
                    logger.debug(f"  List item {i} shape: {v.shape}")
            elif hasattr(self.shap_values, "shape"):
                logger.debug(f"SHAP values shape: {self.shap_values.shape}")
            
            # Extract pos class values
            if isinstance(self.shap_values, list) and len(self.shap_values) == 2:
                self.shap_values = self.shap_values[1]
            elif isinstance(self.shap_values, np.ndarray) and len(self.shap_values.shape) == 3:
                # Shape (samples, features, classes)
                self.shap_values = self.shap_values[:, :, 1]
            elif hasattr(self.shap_values, "values"):
                # Handle Explanation object
                expl_values = self.shap_values.values
                if len(expl_values.shape) == 3:
                    self.shap_values = expl_values[:, :, 1]
                else:
                    self.shap_values = expl_values
            
            # Ensure it's 2D (samples, features)
            if hasattr(self.shap_values, "shape"):
                logger.debug(f"Processed SHAP values shape: {self.shap_values.shape}")

            # Log top features
            self._log_top_features()

            # Generate Plots
            self._save_summary_plot()
            self._save_bar_plot()
            self._save_dependence_plot()

            logger.info(f"Explainability report generated in {self.report_dir}")

        except Exception as e:
            logger.error(f"Failed to generate SHAP report: {e}", exc_info=True)

    def _log_top_features(self) -> None:
        """
        Calculate and log top 5 important features based on mean absolute SHAP values.
        """
        vals = np.abs(self.shap_values).mean(0)
        feature_importance = pd.DataFrame(
            list(zip(self.feature_names, vals)),
            columns=['col_name', 'feature_importance_vals']
        )
        feature_importance.sort_values(by=['feature_importance_vals'], ascending=False, inplace=True)
        
        top_5 = feature_importance.head(5)
        logger.info("Top 5 Important Features (SHAP Mean Absolute Value):")
        for i, row in top_5.iterrows():
            logger.info(f" - {row['col_name']}: {row['feature_importance_vals']:.4f}")
            
        logger.info(f"Mean absolute SHAP value: {vals.mean():.4f}")

    def _save_summary_plot(self) -> None:
        """
        Save SHAP summary plot.
        """
        plt.figure(figsize=(10, 6))
        shap.summary_plot(self.shap_values, self.X_test, feature_names=self.feature_names, show=False)
        plt.tight_layout()
        plt.savefig(self.report_dir / "shap_summary_plot.png")
        plt.close()

    def _save_bar_plot(self) -> None:
        """
        Save SHAP bar plot.
        """
        plt.figure(figsize=(10, 6))
        # shap.plots.bar requires the Explanation object, but we have values
        # We can use summary_plot with plot_type="bar" for compatibility
        shap.summary_plot(self.shap_values, self.X_test, feature_names=self.feature_names, plot_type="bar", show=False)
        plt.tight_layout()
        plt.savefig(self.report_dir / "shap_bar_plot.png")
        plt.close()

    def _save_dependence_plot(self) -> None:
        """
        Save SHAP dependence plot for the top feature.
        """
        vals = np.abs(self.shap_values).mean(0)
        top_feature_idx = np.argmax(vals)
        top_feature_name = self.feature_names[top_feature_idx]
        
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(top_feature_idx, self.shap_values, self.X_test, feature_names=self.feature_names, show=False)
        plt.tight_layout()
        plt.savefig(self.report_dir / f"shap_dependence_plot_{top_feature_name.replace('__', '_')}.png")
        plt.close()
