"""
Model Trainer
Handles model training, evaluation, and saving for different ML algorithms
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, mean_squared_error,
    r2_score, mean_absolute_error
)
import joblib
import yaml
import logging
import os
from typing import Dict, List, Tuple, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns

class ModelTrainer:
    """Trains and evaluates machine learning models"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize model trainer with configuration"""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Model storage
        self.models = {}
        self.best_model = None
        self.best_score = 0
        self.training_history = {}
        
        # Create models directory
        os.makedirs(self.config['data']['models_path'], exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            raise
    
    def get_model(self, algorithm: str, task_type: str = 'classification'):
        """Get a model instance based on algorithm and task type"""
        if task_type == 'classification':
            models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=self.config['model']['random_forest']['n_estimators'],
                    max_depth=self.config['model']['random_forest']['max_depth'],
                    min_samples_split=self.config['model']['random_forest']['min_samples_split'],
                    min_samples_leaf=self.config['model']['random_forest']['min_samples_leaf'],
                    random_state=self.config['model']['random_forest']['random_state']
                ),
                'svm': SVC(random_state=42),
                'logistic_regression': LogisticRegression(random_state=42),
                'neural_network': MLPClassifier(
                    hidden_layer_sizes=tuple(self.config['model']['neural_network']['hidden_layers']),
                    activation=self.config['model']['neural_network']['activation'],
                    learning_rate_init=self.config['model']['neural_network']['learning_rate'],
                    max_iter=self.config['model']['neural_network']['epochs'],
                    random_state=42
                )
            }
        else:  # regression
            models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=self.config['model']['random_forest']['n_estimators'],
                    max_depth=self.config['model']['random_forest']['max_depth'],
                    min_samples_split=self.config['model']['random_forest']['min_samples_split'],
                    min_samples_leaf=self.config['model']['random_forest']['min_samples_leaf'],
                    random_state=self.config['model']['random_forest']['random_state']
                ),
                'svm': SVR(),
                'linear_regression': LinearRegression(),
                'neural_network': MLPRegressor(
                    hidden_layer_sizes=tuple(self.config['model']['neural_network']['hidden_layers']),
                    activation=self.config['model']['neural_network']['activation'],
                    learning_rate_init=self.config['model']['neural_network']['learning_rate'],
                    max_iter=self.config['model']['neural_network']['epochs'],
                    random_state=42
                )
            }
        
        if algorithm not in models:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return models[algorithm]
    
    def prepare_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = None) -> Tuple:
        """Prepare data for training"""
        if test_size is None:
            test_size = self.config['training']['test_size']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=self.config['training']['random_state']
        )
        
        self.logger.info(f"Data split - Train: {X_train.shape}, Test: {X_test.shape}")
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, algorithm: str = None, 
                   task_type: str = None, hyperparameter_tuning: bool = False) -> Dict:
        """Train a model with the specified algorithm"""
        if algorithm is None:
            algorithm = self.config['model']['algorithm']
        if task_type is None:
            task_type = self.config['model']['type']
        
        self.logger.info(f"Training {algorithm} model for {task_type} task...")
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(X, y)
        
        # Get model
        model = self.get_model(algorithm, task_type)
        
        # Hyperparameter tuning if requested
        if hyperparameter_tuning:
            model = self._tune_hyperparameters(model, X_train, y_train, algorithm, task_type)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Evaluate model
        metrics = self._evaluate_model(y_test, y_pred, task_type)
        
        # Store model and results
        model_name = f"{algorithm}_{task_type}"
        self.models[model_name] = {
            'model': model,
            'algorithm': algorithm,
            'task_type': task_type,
            'metrics': metrics,
            'X_test': X_test,
            'y_test': y_test,
            'y_pred': y_pred
        }
        
        # Update best model if necessary
        if task_type == 'classification':
            score = metrics['accuracy']
        else:
            score = metrics['r2_score']
        
        if score > self.best_score:
            self.best_score = score
            self.best_model = model_name
        
        self.logger.info(f"Training complete. Best score: {self.best_score:.4f}")
        
        return {
            'model_name': model_name,
            'metrics': metrics,
            'model': model
        }
    
    def _tune_hyperparameters(self, model, X_train: pd.DataFrame, y_train: pd.Series, 
                             algorithm: str, task_type: str) -> Any:
        """Perform hyperparameter tuning using GridSearchCV"""
        self.logger.info("Performing hyperparameter tuning...")
        
        # Define parameter grids for different algorithms
        if algorithm == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif algorithm == 'svm':
            param_grid = {
                'C': [0.1, 1, 10],
                'gamma': ['scale', 'auto', 0.1, 0.01],
                'kernel': ['rbf', 'linear']
            }
        elif algorithm == 'neural_network':
            param_grid = {
                'hidden_layer_sizes': [(32, 16), (64, 32), (64, 32, 16)],
                'learning_rate_init': [0.001, 0.01, 0.1],
                'alpha': [0.0001, 0.001, 0.01]
            }
        else:
            self.logger.warning(f"Hyperparameter tuning not implemented for {algorithm}")
            return model
        
        # Perform grid search
        scoring = 'accuracy' if task_type == 'classification' else 'r2'
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring=scoring, n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train, y_train)
        
        self.logger.info(f"Best parameters: {grid_search.best_params_}")
        self.logger.info(f"Best score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def _evaluate_model(self, y_true: pd.Series, y_pred: np.ndarray, task_type: str) -> Dict:
        """Evaluate model performance"""
        if task_type == 'classification':
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted'),
                'recall': recall_score(y_true, y_pred, average='weighted'),
                'f1_score': f1_score(y_true, y_pred, average='weighted')
            }
            
            # Add confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            metrics['confusion_matrix'] = cm.tolist()
            
        else:  # regression
            metrics = {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2_score': r2_score(y_true, y_pred)
            }
        
        return metrics
    
    def cross_validate_model(self, X: pd.DataFrame, y: pd.Series, algorithm: str, 
                           task_type: str, cv_folds: int = None) -> Dict:
        """Perform cross-validation"""
        if cv_folds is None:
            cv_folds = self.config['training']['cross_validation_folds']
        
        model = self.get_model(algorithm, task_type)
        scoring = 'accuracy' if task_type == 'classification' else 'r2'
        
        cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
        
        results = {
            'cv_scores': cv_scores.tolist(),
            'mean_score': cv_scores.mean(),
            'std_score': cv_scores.std(),
            'cv_folds': cv_folds
        }
        
        self.logger.info(f"Cross-validation results: {results['mean_score']:.4f} (+/- {results['std_score']:.4f})")
        
        return results
    
    def save_model(self, model_name: str, filepath: str = None):
        """Save a trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        if filepath is None:
            filepath = os.path.join(
                self.config['data']['models_path'], 
                f"{model_name}.joblib"
            )
        
        model_data = self.models[model_name]
        joblib.dump(model_data['model'], filepath)
        
        # Save metrics separately
        metrics_file = filepath.replace('.joblib', '_metrics.json')
        import json
        with open(metrics_file, 'w') as f:
            json.dump(model_data['metrics'], f, indent=2)
        
        self.logger.info(f"Model saved to: {filepath}")
        self.logger.info(f"Metrics saved to: {metrics_file}")
    
    def load_model(self, filepath: str):
        """Load a saved model"""
        model = joblib.load(filepath)
        self.logger.info(f"Model loaded from: {filepath}")
        return model
    
    def get_feature_importance(self, model_name: str) -> Dict:
        """Get feature importance for tree-based models"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]['model']
        
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_names = self.models[model_name]['X_test'].columns
            
            feature_importance = dict(zip(feature_names, importance))
            sorted_importance = dict(sorted(feature_importance.items(), 
                                          key=lambda x: x[1], reverse=True))
            
            return sorted_importance
        else:
            self.logger.warning("Model doesn't support feature importance")
            return {}
    
    def plot_training_results(self, model_name: str, save_path: str = None):
        """Plot training results and metrics"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model_data = self.models[model_name]
        metrics = model_data['metrics']
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Training Results - {model_name}', fontsize=16)
        
        # Plot 1: Metrics comparison
        if model_data['task_type'] == 'classification':
            metric_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
            metric_values = [metrics['accuracy'], metrics['precision'], 
                           metrics['recall'], metrics['f1_score']]
            
            axes[0, 0].bar(metric_names, metric_values, color=['blue', 'green', 'orange', 'red'])
            axes[0, 0].set_title('Classification Metrics')
            axes[0, 0].set_ylim(0, 1)
            
            # Plot 2: Confusion Matrix
            cm = np.array(metrics['confusion_matrix'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 1])
            axes[0, 1].set_title('Confusion Matrix')
            
        else:  # regression
            metric_names = ['MSE', 'RMSE', 'MAE', 'R²']
            metric_values = [metrics['mse'], metrics['rmse'], metrics['mae'], metrics['r2_score']]
            
            axes[0, 0].bar(metric_names, metric_values, color=['blue', 'green', 'orange', 'red'])
            axes[0, 0].set_title('Regression Metrics')
            
            # Plot 2: Actual vs Predicted
            y_test = model_data['y_test']
            y_pred = model_data['y_pred']
            axes[0, 1].scatter(y_test, y_pred, alpha=0.6)
            axes[0, 1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
            axes[0, 1].set_xlabel('Actual Values')
            axes[0, 1].set_ylabel('Predicted Values')
            axes[0, 1].set_title('Actual vs Predicted')
        
        # Plot 3: Feature Importance (if available)
        feature_importance = self.get_feature_importance(model_name)
        if feature_importance:
            top_features = dict(list(feature_importance.items())[:10])
            axes[1, 0].barh(list(top_features.keys()), list(top_features.values()))
            axes[1, 0].set_title('Top 10 Feature Importance')
        
        # Plot 4: Model comparison
        if len(self.models) > 1:
            model_names = list(self.models.keys())
            if model_data['task_type'] == 'classification':
                scores = [self.models[name]['metrics']['accuracy'] for name in model_names]
            else:
                scores = [self.models[name]['metrics']['r2_score'] for name in model_names]
            
            axes[1, 1].bar(model_names, scores)
            axes[1, 1].set_title('Model Comparison')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Training results plot saved to: {save_path}")
        
        plt.show()
    
    def get_training_summary(self) -> Dict:
        """Get a summary of all training results"""
        summary = {
            'total_models': len(self.models),
            'best_model': self.best_model,
            'best_score': self.best_score,
            'models': {}
        }
        
        for name, data in self.models.items():
            summary['models'][name] = {
                'algorithm': data['algorithm'],
                'task_type': data['task_type'],
                'metrics': data['metrics']
            }
        
        return summary

# Example usage
if __name__ == "__main__":
    # Test the model trainer
    trainer = ModelTrainer()
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Classification example
    X_clf = pd.DataFrame({
        'chest_cm': np.random.normal(100, 15, n_samples),
        'waist_cm': np.random.normal(85, 12, n_samples),
        'height_cm': np.random.normal(175, 10, n_samples),
        'weight_kg': np.random.normal(75, 15, n_samples)
    })
    
    # Create target variable (size category)
    chest_values = X_clf['chest_cm'].values
    y_clf = pd.Series(['XS' if x < 90 else 'S' if x < 100 else 'M' if x < 110 else 'L' if x < 120 else 'XL' 
                       for x in chest_values])
    
    # Train classification model
    print("Training classification model...")
    clf_results = trainer.train_model(X_clf, y_clf, 'random_forest', 'classification')
    
    # Regression example
    X_reg = X_clf.copy()
    y_reg = X_clf['chest_cm'] * 0.8 + X_clf['waist_cm'] * 0.6 + np.random.normal(0, 5, n_samples)
    
    print("\nTraining regression model...")
    reg_results = trainer.train_model(X_reg, y_reg, 'random_forest', 'regression')
    
    # Print summary
    print("\nTraining Summary:")
    summary = trainer.get_training_summary()
    print(f"Total models: {summary['total_models']}")
    print(f"Best model: {summary['best_model']}")
    print(f"Best score: {summary['best_score']:.4f}")
    
    # Save models
    trainer.save_model('random_forest_classification')
    trainer.save_model('random_forest_regression')
