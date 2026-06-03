import streamlit as st
import pandas as pd
import sys
import os
import joblib
from pathlib import Path
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.pipeline.prediction_pipeline import PredictionPipeline

# Page Config
st.set_page_config(
    page_title="CardioSense Dashboard",
    page_icon="💓",
    layout="wide"
)

# Title and Description
st.title("💓 CardioSense: Heart Disease Prediction")
st.markdown("""
This dashboard allows you to input patient data and predict the likelihood of heart disease using the machine learning models trained in CardioSense.
""")

# Load Pipeline
@st.cache_resource
def load_pipeline():
    try:
        config_path = project_root / "src" / "config" / "config.yaml"
        pipeline = PredictionPipeline(str(config_path))
        return pipeline
    except Exception as e:
        st.error(f"Failed to load pipeline: {e}")
        return None

pipeline = load_pipeline()

def create_pdf(input_data, prediction, probability, feature_importance):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("CardioSense Heart Disease Prediction Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Prediction Result
    risk_status = "High Risk" if prediction == 1 else "Low Risk"
    prob_text = f"{probability * 100:.1f}%" if probability is not None else "N/A"
    
    elements.append(Paragraph(f"Prediction: {risk_status}", styles['Heading2']))
    elements.append(Paragraph(f"Confidence: {prob_text}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Patient Data Table
    elements.append(Paragraph("Patient Vitals:", styles['Heading3']))
    data = [["Feature", "Value"]]
    for feature, values in input_data.items():
        # Clean up feature name
        clean_name = feature.replace("_", " ").title()
        data.append([clean_name, str(values[0])])
        
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))
    
    # Feature Importance
    if feature_importance is not None:
        elements.append(Paragraph("Key Contributing Factors:", styles['Heading3']))
        imp_data = [["Feature", "Importance"]]
        for item in feature_importance:
            imp_data.append([item['feature'], f"{item['importance']:.4f}"])
            
        t_imp = Table(imp_data)
        t_imp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t_imp)
        
    doc.build(elements)
    buffer.seek(0)
    return buffer


if pipeline:
    st.sidebar.header("Patient Vitals & History")

    # Input Form
    with st.sidebar.form("patient_data_form"):
        # Helper dictionary for mappings
        
        # 1. Age
        age = st.number_input("Age", min_value=0, max_value=120, value=50, step=1)
        
        # 2. Sex (Needed for preprocessor)
        sex_options = {0: "Female", 1: "Male"}
        sex = st.selectbox("Sex", options=list(sex_options.keys()), format_func=lambda x: sex_options[x])
        
        # 3. Chest Pain Type
        cp_options = {
            0: "Typical Angina",
            1: "Atypical Angina",
            2: "Non-anginal Pain",
            3: "Asymptomatic"
        }
        chest_pain_type = st.selectbox("Chest Pain Type", options=list(cp_options.keys()), format_func=lambda x: cp_options[x], index=0)
        
        # 4. Resting Blood Pressure (Needed for preprocessor)
        resting_bp = st.number_input("Resting Blood Pressure (mm Hg)", min_value=50, max_value=250, value=120)
        
        # 5. Cholesterol
        cholesterol = st.number_input("Cholesterol (mg/dl)", min_value=0, max_value=600, value=200)
        
        # 6. Fasting Blood Sugar
        fbs_options = {0: "No (< 120 mg/dl)", 1: "Yes (> 120 mg/dl)"}
        fasting_blood_sugar = st.selectbox("Fasting Blood Sugar > 120 mg/dl", options=list(fbs_options.keys()), format_func=lambda x: fbs_options[x])
        
        # 7. Resting ECG
        restecg_options = {
            0: "Normal",
            1: "ST-T wave abnormality",
            2: "Left ventricular hypertrophy"
        }
        resting_ecg = st.selectbox("Resting ECG Result", options=list(restecg_options.keys()), format_func=lambda x: restecg_options[x])
        
        # 8. Max Heart Rate (Needed for preprocessor)
        max_heart_rate = st.number_input("Max Heart Rate Achieved", min_value=50, max_value=250, value=150)
        
        # 9. Exercise Induced Angina
        exang_options = {0: "No", 1: "Yes"}
        exercise_angina = st.selectbox("Exercise Induced Angina", options=list(exang_options.keys()), format_func=lambda x: exang_options[x])
        
        # 10. ST Depression (Oldpeak)
        st_depression = st.number_input("ST Depression (Oldpeak)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
        
        # 11. ST Slope
        slope_options = {
            0: "Upsloping",
            1: "Flat",
            2: "Downsloping"
        }
        st_slope = st.selectbox("Slope of Peak Exercise ST Segment", options=list(slope_options.keys()), format_func=lambda x: slope_options[x], index=0)
        
        # 12. Number of Major Vessels
        num_major_vessels = st.slider("Number of Major Vessels Colored by Flourosopy (0-4)", 0, 4, 0)
        
        # 13. Thalassemia
        thal_options = {
            0: "Unknown/Null",
            1: "Before Fixed Defect",
            2: "Fixed Defect",
            3: "Reversible Defect"
        }
        thalassemia = st.selectbox("Thalassemia", options=list(thal_options.keys()), format_func=lambda x: thal_options[x], index=2)
        
        submitted = st.form_submit_button("Predict Heart Disease Risk")

    if submitted:
        # Create DataFrame with normalized column names expected by Preprocessor
        input_data = {
            'age': [age],
            'sex': [sex],
            'chest_pain_type': [chest_pain_type],
            'resting_bp': [resting_bp],
            'cholesterol': [cholesterol],
            'fasting_blood_sugar': [fasting_blood_sugar],
            'resting_ecg': [resting_ecg],
            'max_heart_rate': [max_heart_rate],
            'exercise_angina': [exercise_angina],
            'st_depression': [st_depression],
            'st_slope': [st_slope],
            'num_major_vessels': [num_major_vessels],
            'thalassemia': [thalassemia]
        }
        
        input_df = pd.DataFrame(input_data)
        
        # Show input data
        with st.expander("View Input Data"):
            st.dataframe(input_df)

        try:
            # Make Prediction
            with st.spinner("Processing data and generating prediction..."):
                results = pipeline.predict(input_df)
                
            prediction = results["prediction"].iloc[0]
            probability = results["probability"].iloc[0]
            
            # Display Results
            st.divider()
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Prediction Result")
                if prediction == 1:
                    st.error(f"**High Risk of Heart Disease**")
                else:
                    st.success(f"**Low Risk of Heart Disease**")
                    
            with col2:
                st.subheader("Confidence Score")
                if probability is not None:
                    prob_pct = probability * 100
                    st.metric("Probability", f"{prob_pct:.1f}%")
                    st.progress(probability)
                else:
                    st.info("Probability not available for this model.")
            
            # Model Explainability (SHAP)
            st.divider()
            st.subheader("Why this prediction?")
            st.write("Top factors contributing to this result:")
            
            try:
                importance = pipeline.get_feature_importance(input_df)
                importance_source = "SHAP"
            except Exception as e:
                logger.error(f"SHAP explanation error: {e}", exc_info=True)
                importance = pipeline.get_model_feature_importance()
                importance_source = "model"
                if importance:
                    st.warning(
                        "SHAP explanations are unavailable in this environment, "
                        "so model-native feature importance is shown instead."
                    )
                else:
                    st.warning(f"Could not generate explanation: {e}")
                    importance = None
                
            if importance:
                # Format for chart
                imp_df = pd.DataFrame(importance)
                
                # Simple bar chart
                st.bar_chart(imp_df.set_index("feature"))
                
                # Detailed table
                with st.expander("Detailed Contribution Data"):
                    st.caption(f"Source: {importance_source}")
                    st.table(imp_df)

            # PDF Download
            st.divider()
            pdf_buffer = create_pdf(input_data, prediction, probability, importance)
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name="cardiosense_report.pdf",
                mime="application/pdf"
            )
                
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")
            logger.error(f"Prediction error: {e}", exc_info=True)

else:
    st.warning("Please check your configuration and ensure trained models are available.")
