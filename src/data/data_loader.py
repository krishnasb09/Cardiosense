import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import List

logger = logging.getLogger(__name__)

def load_all_data(data_dir: str = "data/raw") -> pd.DataFrame:
    """
    Load all CSV files from a directory and merge them.
    
    Args:
        data_dir (str): Path to the directory containing raw CSV files.
        
    Returns:
        pd.DataFrame: Combined DataFrame.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        logger.error(f"Data directory not found: {data_dir}")
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
    csv_files = list(data_path.glob("*.csv"))
    if not csv_files:
        logger.warning(f"No CSV files found in {data_dir}")
        return pd.DataFrame()
        
    all_dfs = []
    for file in csv_files:
        logger.info(f"Loading data from {file.name}")
        df = pd.read_csv(file)
        
        # Normalize column names
        column_mapping = {
            'age': 'age', 'Age': 'age',
            'sex': 'sex', 'Sex': 'sex',
            'cp': 'chest_pain_type', 'chest pain type': 'chest_pain_type', 'Chest pain type': 'chest_pain_type',
            'trestbps': 'resting_bp', 'resting bp s': 'resting_bp', 'BP': 'resting_bp',
            'chol': 'cholesterol', 'cholesterol': 'cholesterol', 'Cholesterol': 'cholesterol',
            'fbs': 'fasting_blood_sugar', 'fasting blood sugar': 'fasting_blood_sugar', 'FBS': 'fasting_blood_sugar',
            'restecg': 'resting_ecg', 'resting ecg': 'resting_ecg', 'EKG results': 'resting_ecg',
            'thalach': 'max_heart_rate', 'max heart rate': 'max_heart_rate', 'Max HR': 'max_heart_rate',
            'exang': 'exercise_angina', 'exercise angina': 'exercise_angina', 'Exercise angina': 'exercise_angina',
            'oldpeak': 'st_depression', 'ST depression': 'st_depression',
            'slope': 'st_slope', 'ST slope': 'st_slope', 'Slope of ST': 'st_slope',
            'ca': 'num_major_vessels', 'Number of vessels fluro': 'num_major_vessels',
            'thal': 'thalassemia', 'Thallium': 'thalassemia'
        }
        
        # Strip and map columns
        df.columns = [col.strip() for col in df.columns]
        new_columns = {}
        for col in df.columns:
            if col in column_mapping:
                new_columns[col] = column_mapping[col]
            elif col.lower() in ['target', 'heart disease', 'heart_disease', 'diagnosis']:
                new_columns[col] = 'target'
        
        df = df.rename(columns=new_columns)
        
        # Keep only normalized columns and target
        expected_cols = list(set(column_mapping.values())) + ['target']
        df = df[[col for col in df.columns if col in expected_cols]]
            
        # Ensure target is numeric
        # Handle string target values
        mapping = {
            'presence': 1, 'absence': 0,
            'positive': 1, 'negative': 0,
            '1': 1, '0': 0,
            '1.0': 1, '0.0': 0
        }
        
        def map_target(val):
            if pd.isna(val):
                return val
            if isinstance(val, (int, float, np.integer, np.floating)):
                return int(val)
            if isinstance(val, str):
                s = val.strip().lower()
                if s in mapping:
                    return mapping[s]
            return val

        df['target'] = df['target'].apply(map_target)
        
        # Drop rows with NaN in target
        if df['target'].isnull().any():
            logger.warning(f"Dropping {df['target'].isnull().sum()} rows with null target in {file.name}")
            df = df.dropna(subset=['target'])
            
        df['target'] = df['target'].astype(int)
        all_dfs.append(df)

        
    combined_df = pd.concat(all_dfs, axis=0, ignore_index=True, sort=False)
    logger.info(f"Combined dataset shape: {combined_df.shape}")
    
    return combined_df
