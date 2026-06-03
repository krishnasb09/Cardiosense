import pandas as pd
import sys
from pathlib import Path

# Add project root to sys.path for direct execution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.pipeline.prediction_pipeline import PredictionPipeline

def main():
    # Initialize pipeline
    pipeline = PredictionPipeline(config_path="src/config/config.yaml")

    # -----------------------------
    # Test 1: Single patient input
    # -----------------------------
    single_patient = {
        "age": [55],
        "sex": [1],
        "chest_pain_type": [3],
        "resting_bp": [140],
        "cholesterol": [250],
        "fasting_blood_sugar": [0],
        "resting_ecg": [1],
        "max_heart_rate": [150],
        "exercise_angina": [0],
        "st_depression": [1.2],
        "st_slope": [2],
        "num_major_vessels": [0],
        "thalassemia": [3]
    }

    X_single = pd.DataFrame(single_patient)
    result_single = pipeline.predict(X_single)
    print("Single Patient Prediction:")
    print(result_single)

    # Explain single patient
    pipeline.explain(X_single)
    print("SHAP explanation generated for single patient.\n")

    # -----------------------------
    # Test 2: Batch input (5 patients)
    # -----------------------------
    batch_data = {
        "age": [50, 60, 45, 65, 70],
        "sex": [1, 0, 1, 0, 1],
        "chest_pain_type": [3, 2, 4, 1, 3],
        "resting_bp": [130, 150, 120, 140, 135],
        "cholesterol": [230, 260, 210, 280, 245],
        "fasting_blood_sugar": [0, 1, 0, 1, 0],
        "resting_ecg": [1, 0, 1, 0, 1],
        "max_heart_rate": [160, 140, 170, 130, 150],
        "exercise_angina": [0, 1, 0, 1, 0],
        "st_depression": [1.0, 2.0, 0.5, 1.5, 1.2],
        "st_slope": [2, 3, 2, 1, 2],
        "num_major_vessels": [0, 2, 0, 3, 1],
        "thalassemia": [3, 2, 3, 1, 3]
    }

    X_batch = pd.DataFrame(batch_data)
    result_batch = pipeline.predict(X_batch)
    print("Batch Prediction (5 patients):")
    print(result_batch)

    # Explain batch predictions
    pipeline.explain(X_batch)
    print("SHAP explanation generated for batch input.\n")

    # -----------------------------
    # Save batch predictions (optional)
    # -----------------------------
    output_path = Path("data/processed/predictions.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_batch.to_csv(output_path, index=False)
    print(f"Batch predictions saved to {output_path}")

if __name__ == "__main__":
    main()