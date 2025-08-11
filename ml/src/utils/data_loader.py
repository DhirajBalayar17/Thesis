"""
Data Loader
Handles loading and validation of datasets from various sources
"""

import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class DataLoader:
    """Loads and validates datasets for ML training"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize data loader with configuration"""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Data paths
        self.raw_path = self.config.get('data', {}).get('raw_path', 'data/raw/')
        self.processed_path = self.config.get('data', {}).get('processed_path', 'data/processed/')
        self.images_path = self.config.get('data', {}).get('images_path', 'data/images/')
        self.supported_formats = self.config.get('data', {}).get('supported_formats', ['.csv', '.xlsx', '.xls'])
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in config file: {e}")
            return {}
    
    def list_available_datasets(self) -> List[str]:
        """List all available dataset files in raw data directory"""
        try:
            if not os.path.exists(self.raw_path):
                self.logger.warning(f"Raw data directory not found: {self.raw_path}")
                return []
            
            datasets = []
            for file in os.listdir(self.raw_path):
                if any(file.endswith(fmt) for fmt in self.supported_formats):
                    datasets.append(file)
            
            return sorted(datasets)
            
        except Exception as e:
            self.logger.error(f"Error listing datasets: {e}")
            return []
    
    def load_dataset(self, filename: str) -> Optional[pd.DataFrame]:
        """Load a single dataset file"""
        try:
            file_path = os.path.join(self.raw_path, filename)
            
            if not os.path.exists(file_path):
                self.logger.error(f"Dataset file not found: {file_path}")
                return None
            
            # Load based on file extension
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif filename.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                self.logger.error(f"Unsupported file format: {filename}")
                return None
            
            self.logger.info(f"Loaded dataset {filename}: {df.shape}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading dataset {filename}: {e}")
            return None
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all available datasets"""
        datasets = {}
        available_files = self.list_available_datasets()
        
        for filename in available_files:
            df = self.load_dataset(filename)
            if df is not None:
                # Use filename without extension as key
                key = os.path.splitext(filename)[0]
                datasets[key] = df
        
        self.logger.info(f"Successfully loaded {len(datasets)} datasets")
        return datasets
    
    def validate_dataset(self, df: pd.DataFrame, name: str = "dataset") -> Dict:
        """Validate dataset structure and quality"""
        validation = {
            'name': name,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'is_valid': True,
            'issues': []
        }
        
        # Check for critical issues
        if df.empty:
            validation['is_valid'] = False
            validation['issues'].append("Dataset is empty")
        
        if len(df.columns) < 2:
            validation['issues'].append("Dataset has too few columns")
        
        # Check for high missing values
        for col, missing_pct in validation['missing_percentage'].items():
            if missing_pct > 80:
                validation['issues'].append(f"Column '{col}' has {missing_pct:.1f}% missing values")
        
        if validation['issues']:
            validation['is_valid'] = False
        
        return validation
    
    def get_dataset_info(self, df: pd.DataFrame, name: str = "dataset") -> Dict:
        """Get comprehensive dataset information"""
        info = self.validate_dataset(df, name)
        
        # Add additional analysis
        info.update({
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns),
            'date_columns': list(df.select_dtypes(include=['datetime']).columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'unique_values': {col: df[col].nunique() for col in df.columns}
        })
        
        return info
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> bool:
        """Save processed data to the processed data directory"""
        try:
            if not os.path.exists(self.processed_path):
                os.makedirs(self.processed_path, exist_ok=True)
            
            file_path = os.path.join(self.processed_path, filename)
            
            if filename.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif filename.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            elif filename.endswith('.json'):
                df.to_json(file_path, orient='records')
            else:
                # Default to CSV
                df.to_csv(file_path, index=False)
            
            self.logger.info(f"Processed data saved to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving processed data: {e}")
            return False
