# CardioSense: CAD Risk Prediction System

CardioSense is a comprehensive machine learning solution for predicting Coronary Artery Disease (CAD) risk using clinical data.

## Project Structure

```text
cardiosense/
├── data/                       # Data storage
│   ├── raw/                    # Original clinical datasets
│   ├── processed/              # Preprocessed features and predictions
│   └── external/               # Third-party data
├── notebooks/                  # Documentation and Research
│   ├── 01_eda.ipynb            # Exploratory Data Analysis
│   ├── 02_feature_selection.ipynb # Feature Selection experiments
│   ├── 03_model_comparison.ipynb  # Training and Evaluation
│   └── 04_explainability.ipynb    # SHAP and Interpretability
├── src/                        # Core Library
│   ├── config/                 # Configuration files
│   ├── data/                   # Data ingestion and preprocessing
│   ├── features/               # Feature selection and engineering
│   ├── models/                 # Model factory and selection
│   ├── explainability/         # Model interpretability (SHAP)
│   ├── pipeline/               # Production pipelines
│   ├── utils/                  # Core utilities
│   └── main.py                 # CLI entry point
├── web/                        # Web Application
│   ├── backend/                # Flask API
│   └── frontend/               # React Dashboard
├── experiments/                # Research tracking
├── models/                     # Saved artifacts
│   ├── trained_models/         # Serialized models
│   └── model_metadata/         # Selection metrics
├── reports/                    # Visualizations and reports
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## Quick Start

### 1. Installation
```powershell
pip install -r requirements.txt
```

### 2. Run Pipelines
- **Train Models**: `python src/pipeline/training_pipeline.py`
- **Verify/Predict**: `python src/pipeline/testing_pipeline.py`
