import matplotlib.pyplot as plt
import json
import os
import numpy as np

def load_cardiosense_metrics():
    # Path to the metrics file
    metrics_path = os.path.join(os.path.dirname(__file__), '../../reports/evaluation_reports/evaluation_metrics.json')
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    # We'll use Random Forest or XGBoost as our champion model. 
    # Based on the file, Random Forest and XGBoost both have ~0.95 accuracy.
    # We'll use the highest one.
    
    best_accuracy = 0
    for model_name, data in metrics.items():
        if data['accuracy'] > best_accuracy:
            best_accuracy = data['accuracy']
            
    return best_accuracy

def generate_graph():
    # 1. Get Our Model's Performance
    our_accuracy = load_cardiosense_metrics()
    
    # 2. Define Existing Models Performance (from the provided PDF/Image)
    # Using values from Table 5 (Z-Alizadeh Sani dataset) which seemed to be the best performing competitor
    existing_models = {
        'Existing: RF + BESO': 0.92,
        'Existing: LR + BESO': 0.90,
        'Existing: SVM + BESO': 0.89
    }
    
    # 3. Prepare Data for Plotting
    models = list(existing_models.keys()) + ['CardioSense (Ours)']
    accuracies = list(existing_models.values()) + [our_accuracy]
    
    # Colors: Grey for existing, Blue/Highlight for ours
    colors = ['#bdc3c7'] * len(existing_models) + ['#3498db']
    
    # 4. Create Plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(models, accuracies, color=colors, width=0.6)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom', fontweight='bold')
    
    plt.ylabel('Accuracy')
    plt.title('Model Performance Comparison: CardioSense vs Existing Approaches')
    plt.ylim(0, 1.1)  # Scale from 0 to 1.1 to leave room for text
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the plot
    output_path = os.path.join(os.path.dirname(__file__), '../../reports/model_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_graph()
