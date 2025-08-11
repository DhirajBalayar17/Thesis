#!/usr/bin/env python3
"""
Prediction Script for Fashion AI Thesis
Test trained models
"""

import os
import sys
import json
import argparse
import yaml
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.data_loader import DataLoader
from src.preprocessing.data_preprocessor import DataPreprocessor
from src.training.model_trainer import ModelTrainer

def load_config(config_path: str = 'config/config.yaml'):
    """Load configuration file"""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in config file: {e}")
        return None

def main():
    """Main prediction function"""
    parser = argparse.ArgumentParser(description='Test trained ML models for Fashion AI Thesis')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--model', help='Model name to use for prediction')
    parser.add_argument('--input', help='Input data file (CSV, JSON)')
    parser.add_argument('--sample', action='store_true', help='Use sample data for prediction')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        sys.exit(1)
    
    print("🔮 Fashion AI Thesis - Model Prediction")
    print("=" * 50)
    
    try:
        # Initialize components
        print("Initializing ML components...")
        data_loader = DataLoader(args.config)
        preprocessor = DataPreprocessor(args.config)
        trainer = ModelTrainer(args.config)
        
        # List available models
        models_path = config['data']['models_path']
        if not os.path.exists(models_path):
            print(f"❌ Models directory not found: {models_path}")
            print("Please train a model first using train.py")
            sys.exit(1)
        
        model_files = [f for f in os.listdir(models_path) if f.endswith('.joblib') and not f.endswith('_preprocessor.joblib')]
        
        if not model_files:
            print("❌ No trained models found!")
            print("Please train a model first using train.py")
            sys.exit(1)
        
        print(f"📊 Found {len(model_files)} trained models:")
        for i, model_file in enumerate(model_files):
            model_name = model_file.replace('.joblib', '')
            print(f"  {i+1}. {model_name}")
        
        # Select model
        if args.model:
            selected_model = args.model
            if not any(selected_model in f for f in model_files):
                print(f"❌ Model '{selected_model}' not found!")
                sys.exit(1)
        else:
            if len(model_files) == 1:
                selected_model = model_files[0].replace('.joblib', '')
            else:
                try:
                    choice = int(input(f"\nSelect a model (1-{len(model_files)}): ")) - 1
                    if 0 <= choice < len(model_files):
                        selected_model = model_files[choice].replace('.joblib', '')
                    else:
                        print("❌ Invalid choice!")
                        sys.exit(1)
                except (ValueError, KeyboardInterrupt):
                    print("\n❌ Invalid input!")
                    sys.exit(1)
        
        print(f"\n🎯 Selected model: {selected_model}")
        
        # Load model
        model_path = os.path.join(models_path, f"{selected_model}.joblib")
        model = trainer.load_model(model_path)
        
        # Load preprocessor
        preprocessor_path = os.path.join(models_path, f"{selected_model}_preprocessor.joblib")
        if os.path.exists(preprocessor_path):
            preprocessor.load_preprocessor(preprocessor_path)
            print("✅ Preprocessor loaded")
        else:
            print("⚠️  No preprocessor found, using default preprocessing")
        
        # Load metrics
        metrics_path = os.path.join(models_path, f"{selected_model}_metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            print("✅ Model metrics loaded")
            print(f"   Performance: {metrics.get('accuracy', metrics.get('r2_score', 'N/A')):.4f}")
        
        # Prepare input data
        if args.input:
            # Load from file
            if args.input.endswith('.csv'):
                input_data = pd.read_csv(args.input)
            elif args.input.endswith('.json'):
                input_data = pd.read_json(args.input)
            else:
                print(f"❌ Unsupported file format: {args.input}")
                sys.exit(1)
            print(f"📁 Loaded input data from: {args.input}")
        elif args.sample:
            # Use sample data
            print("📝 Using sample data for prediction...")
            
            # Create sample data based on model type
            if 'classification' in selected_model:
                input_data = pd.DataFrame({
                    'chest_cm': [95, 100, 105, 110, 115],
                    'waist_cm': [80, 85, 90, 95, 100],
                    'height_cm': [170, 175, 180, 185, 190],
                    'weight_kg': [70, 75, 80, 85, 90],
                    'age': [25, 30, 35, 40, 45],
                    'shoulder_cm': [45, 47, 49, 51, 53],
                    'hip_cm': [95, 100, 105, 110, 115],
                    'style': ['casual', 'formal', 'casual', 'formal', 'casual'],
                    'fit': ['regular', 'slim', 'regular', 'slim', 'regular'],
                    'occasion': ['daily', 'work', 'daily', 'work', 'daily'],
                    'brand_preference': ['brand1', 'brand2', 'brand1', 'brand2', 'brand1']
                })
            else:  # regression
                input_data = pd.DataFrame({
                    'chest_cm': [95, 100, 105, 110, 115],
                    'waist_cm': [80, 85, 90, 95, 100],
                    'height_cm': [170, 175, 180, 185, 190],
                    'weight_kg': [70, 75, 80, 85, 90],
                    'age': [25, 30, 35, 40, 45],
                    'shoulder_cm': [45, 47, 49, 51, 53],
                    'hip_cm': [95, 100, 105, 110, 115],
                    'style': ['casual', 'formal', 'casual', 'formal', 'casual'],
                    'fit': ['regular', 'slim', 'regular', 'slim', 'regular'],
                    'occasion': ['daily', 'work', 'daily', 'work', 'daily'],
                    'brand_preference': ['brand1', 'brand2', 'brand1', 'brand2', 'brand1']
                })
        else:
            # Interactive input
            print("📝 Enter input data manually:")
            input_data = {}
            
            # Get column names from preprocessor or use defaults
            default_columns = ['chest_cm', 'waist_cm', 'height_cm', 'weight_kg', 'age', 'shoulder_cm', 'hip_cm']
            categorical_columns = ['style', 'fit', 'occasion', 'brand_preference']
            
            # Get numeric values
            for col in default_columns:
                try:
                    value = float(input(f"Enter {col}: "))
                    input_data[col] = value
                except (ValueError, KeyboardInterrupt):
                    print(f"❌ Invalid input for {col}!")
                    sys.exit(1)
            
            # Get categorical values
            for col in categorical_columns:
                try:
                    value = input(f"Enter {col} (options: casual/formal, regular/slim, daily/work, brand1/brand2): ")
                    input_data[col] = value
                except (KeyboardInterrupt):
                    print(f"❌ Invalid input for {col}!")
                    sys.exit(1)
            
            input_data = pd.DataFrame([input_data])
        
        print(f"\n📊 Input data shape: {input_data.shape}")
        print("Input data:")
        print(input_data)
        
        # Preprocess input data
        print("\n🔄 Preprocessing input data...")
        X_processed, _ = preprocessor.preprocess_data(input_data)
        
        print(f"Processed data shape: {X_processed.shape}")
        print("Processed features:")
        print(X_processed.head())
        
        # Make prediction
        print("\n🔮 Making predictions...")
        prediction = model.predict(X_processed)
        
        # Get prediction probabilities if available
        prediction_proba = None
        if hasattr(model, 'predict_proba'):
            prediction_proba = model.predict_proba(X_processed)
        
        # Display results
        print("\n" + "=" * 50)
        print("🎯 PREDICTION RESULTS")
        print("=" * 50)
        
        print(f"Model used: {selected_model}")
        print(f"Input samples: {len(input_data)}")
        print(f"Predictions: {prediction}")
        
        if prediction_proba is not None:
            print(f"Prediction probabilities: {prediction_proba}")
        
        # Format predictions nicely
        if 'classification' in selected_model:
            print("\n📋 Classification Results:")
            for i, pred in enumerate(prediction):
                print(f"  Sample {i+1}: {pred}")
                if prediction_proba is not None:
                    print(f"    Confidence: {max(prediction_proba[i]):.2%}")
        else:
            print("\n📊 Regression Results:")
            for i, pred in enumerate(prediction):
                print(f"  Sample {i+1}: {pred:.2f}")
        
        print("\n✅ Prediction completed successfully!")
        
        # Save results
        results = {
            'model_used': selected_model,
            'input_data': input_data.to_dict('records'),
            'predictions': prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            'prediction_probabilities': prediction_proba.tolist() if prediction_proba is not None else None,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        results_path = os.path.join(
            config['data']['models_path'], 
            f"{selected_model}_prediction_results.json"
        )
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {results_path}")
        
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
