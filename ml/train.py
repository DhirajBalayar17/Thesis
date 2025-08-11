#!/usr/bin/env python3
"""
Main Training Script for Fashion AI Thesis
Orchestrates the complete ML training pipeline
"""

import os
import sys
import logging
import argparse
import yaml
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.data_loader import DataLoader
from src.preprocessing.data_preprocessor import DataPreprocessor
from src.training.model_trainer import ModelTrainer

def setup_logging(log_level: str = 'INFO'):
    """Setup logging configuration"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'training_{timestamp}.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def load_config(config_path: str = 'config/config.yaml'):
    """Load configuration file"""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in config file: {e}")
        sys.exit(1)

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train ML models for Fashion AI Thesis')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--algorithm', help='ML algorithm to use (overrides config)')
    parser.add_argument('--task-type', help='Task type: classification or regression (overrides config)')
    parser.add_argument('--hyperparameter-tuning', action='store_true', help='Enable hyperparameter tuning')
    parser.add_argument('--cross-validation', action='store_true', help='Enable cross-validation')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting Fashion AI Thesis ML Training Pipeline")
    
    # Load configuration
    config = load_config(args.config)
    logger.info(f"Configuration loaded from {args.config}")
    
    try:
        # Initialize components
        logger.info("Initializing ML components...")
        data_loader = DataLoader(args.config)
        preprocessor = DataPreprocessor(args.config)
        trainer = ModelTrainer(args.config)
        
        # List available datasets
        logger.info("Scanning for available datasets...")
        available_datasets = data_loader.list_available_datasets()
        
        if not available_datasets:
            logger.error("No datasets found in data/raw/ directory!")
            logger.info("Please place your dataset files in the data/raw/ directory")
            sys.exit(1)
        
        logger.info(f"Found {len(available_datasets)} datasets: {available_datasets}")
        
        # Load all datasets
        datasets = data_loader.load_all_datasets()
        
        # Analyze each dataset
        for name, df in datasets.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Analyzing dataset: {name}")
            logger.info(f"{'='*50}")
            
            # Get dataset info
            info = data_loader.get_dataset_info(df, name)
            logger.info(f"Shape: {info['shape']}")
            logger.info(f"Columns: {info['columns']}")
            logger.info(f"Memory usage: {info['memory_usage'] / 1024:.2f} KB")
            
            # Validate dataset
            validation = data_loader.validate_dataset(df)
            if not validation['is_valid']:
                logger.error(f"Dataset {name} validation failed:")
                for issue in validation['issues']:
                    logger.error(f"  - {issue}")
                continue
            
            # Log any validation issues as warnings
            if validation['issues']:
                logger.warning(f"Dataset {name} has validation issues:")
                for issue in validation['issues']:
                    logger.warning(f"  - {issue}")
            
            # Log dataset statistics
            logger.info(f"Dataset {name} statistics:")
            logger.info(f"  - Total rows: {validation['shape'][0]}")
            logger.info(f"  - Total columns: {validation['shape'][1]}")
            logger.info(f"  - Duplicate rows: {validation['duplicate_rows']}")
            logger.info(f"  - Missing values: {sum(validation['missing_values'].values())}")
            
            # Preprocess dataset
            logger.info(f"Preprocessing dataset: {name}")
            
            # Determine target column (you may need to customize this)
            target_column = None
            potential_targets = ['size', 'size_category', 'fit', 'style', 'target', 'label', 'class']
            
            for col in potential_targets:
                if col in df.columns:
                    target_column = col
                    break
            
            if target_column:
                logger.info(f"Using '{target_column}' as target column")
            else:
                logger.warning(f"No target column found in {name}, skipping training")
                continue
            
            # Preprocess data
            X, y = preprocessor.preprocess_data(df, target_column)
            
            # Determine task type
            if y is not None:
                if y.dtype == 'object' or y.dtype.name == 'category':
                    task_type = 'classification'
                    logger.info(f"Detected classification task with {y.nunique()} unique classes")
                else:
                    task_type = 'regression'
                    logger.info(f"Detected regression task")
            else:
                logger.warning("No target variable found, skipping training")
                continue
            
            # Override task type if specified
            if args.task_type:
                task_type = args.task_type
                logger.info(f"Task type overridden to: {task_type}")
            
            # Determine algorithm
            algorithm = args.algorithm if args.algorithm else config['model']['algorithm']
            logger.info(f"Using algorithm: {algorithm}")
            
            # Perform cross-validation if requested
            if args.cross_validation:
                logger.info("Performing cross-validation...")
                cv_results = trainer.cross_validate_model(X, y, algorithm, task_type)
                logger.info(f"Cross-validation results: {cv_results['mean_score']:.4f} (+/- {cv_results['std_score']:.4f})")
            
            # Train model
            logger.info(f"Training {algorithm} model for {task_type} task...")
            training_results = trainer.train_model(
                X, y, 
                algorithm=algorithm, 
                task_type=task_type,
                hyperparameter_tuning=args.hyperparameter_tuning
            )
            
            # Display results
            logger.info(f"Training completed for {training_results['model_name']}")
            logger.info("Metrics:")
            for metric, value in training_results['metrics'].items():
                if metric != 'confusion_matrix':  # Skip confusion matrix in logs
                    logger.info(f"  {metric}: {value:.4f}")
            
            # Save model
            trainer.save_model(training_results['model_name'])
            
            # Save preprocessor
            preprocessor_path = os.path.join(
                config['data']['models_path'], 
                f"{training_results['model_name']}_preprocessor.joblib"
            )
            preprocessor.save_preprocessor(preprocessor_path)
            
            # Save processed data
            processed_data_path = os.path.join(
                config['data']['processed_path'], 
                f"{name}_processed.csv"
            )
            data_loader.save_processed_data(X, f"{name}_processed.csv")
            
            logger.info(f"Model and preprocessor saved successfully")
        
        # Generate training summary
        logger.info("\n" + "="*60)
        logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
        summary = trainer.get_training_summary()
        logger.info(f"Total models trained: {summary['total_models']}")
        logger.info(f"Best model: {summary['best_model']}")
        logger.info(f"Best score: {summary['best_score']:.4f}")
        
        # Save training summary
        summary_path = os.path.join(
            config['data']['models_path'], 
            f"training_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        import json
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Training summary saved to: {summary_path}")
        
        # Plot results for best model
        if summary['best_model']:
            logger.info(f"Generating plots for best model: {summary['best_model']}")
            plot_path = os.path.join(
                config['data']['models_path'], 
                f"{summary['best_model']}_results.png"
            )
            trainer.plot_training_results(summary['best_model'], plot_path)
        
        logger.info("\n🎉 Training pipeline completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Review the generated plots and metrics")
        logger.info("2. Test the trained models using predict.py")
        logger.info("3. Start the ML API server using app.py")
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
