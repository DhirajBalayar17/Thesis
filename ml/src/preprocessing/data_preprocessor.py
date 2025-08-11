"""
Data Preprocessor
Handles data cleaning, feature engineering, and preparation for ML training
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import logging
from typing import Dict, List, Tuple, Optional
import yaml

class DataPreprocessor:
    """Preprocesses data for machine learning"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize preprocessor with configuration"""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Preprocessing components
        self.scaler = None
        self.label_encoders = {}
        self.onehot_encoder = None
        self.imputer = None
        self.preprocessor = None
        
        # Store column information
        self.numeric_columns = []
        self.categorical_columns = []
        self.target_column = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            raise
    
    def analyze_data(self, df: pd.DataFrame) -> Dict:
        """Analyze data structure and provide preprocessing recommendations"""
        analysis = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'unique_values': {col: df[col].nunique() for col in df.columns},
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns),
            'recommendations': []
        }
        
        # Generate recommendations
        for col in df.columns:
            missing_pct = analysis['missing_percentage'][col]
            unique_count = analysis['unique_values'][col]
            
            if missing_pct > 50:
                analysis['recommendations'].append(f"Column '{col}' has {missing_pct:.1f}% missing values - consider dropping")
            elif missing_pct > 0:
                analysis['recommendations'].append(f"Column '{col}' has {missing_pct:.1f}% missing values - needs imputation")
            
            if col in analysis['categorical_columns'] and unique_count > 50:
                analysis['recommendations'].append(f"Column '{col}' has {unique_count} unique values - consider encoding strategy")
        
        return analysis
    
    def identify_column_types(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Identify numeric and categorical columns"""
        self.numeric_columns = list(df.select_dtypes(include=['number']).columns)
        self.categorical_columns = list(df.select_dtypes(include=['object', 'category']).columns)
        
        self.logger.info(f"Identified {len(self.numeric_columns)} numeric columns: {self.numeric_columns}")
        self.logger.info(f"Identified {len(self.categorical_columns)} categorical columns: {self.categorical_columns}")
        
        return self.numeric_columns, self.categorical_columns
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """Handle missing values in the dataset"""
        df_clean = df.copy()
        
        if strategy == 'auto':
            # Use different strategies for different column types
            for col in df_clean.columns:
                if col in self.numeric_columns:
                    if df_clean[col].isnull().sum() > 0:
                        df_clean[col].fillna(df_clean[col].median(), inplace=True)
                elif col in self.categorical_columns:
                    if df_clean[col].isnull().sum() > 0:
                        df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
        
        elif strategy == 'drop':
            df_clean.dropna(inplace=True)
        
        elif strategy == 'interpolate':
            df_clean.interpolate(method='linear', inplace=True)
        
        missing_count = df_clean.isnull().sum().sum()
        self.logger.info(f"Missing values after cleaning: {missing_count}")
        
        return df_clean
    
    def encode_categorical_variables(self, df: pd.DataFrame, method: str = 'label') -> pd.DataFrame:
        """Encode categorical variables"""
        df_encoded = df.copy()
        
        if method == 'label':
            # Label encoding for categorical columns
            for col in self.categorical_columns:
                if col in df_encoded.columns:
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                    self.label_encoders[col] = le
                    self.logger.info(f"Label encoded column: {col}")
        
        elif method == 'onehot':
            # One-hot encoding for categorical columns
            for col in self.categorical_columns:
                if col in df_encoded.columns:
                    dummies = pd.get_dummies(df_encoded[col], prefix=col)
                    df_encoded = pd.concat([df_encoded, dummies], axis=1)
                    df_encoded.drop(col, axis=1, inplace=True)
                    self.logger.info(f"One-hot encoded column: {col}")
        
        return df_encoded
    
    def scale_numeric_features(self, df: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
        """Scale numeric features"""
        df_scaled = df.copy()
        
        if method == 'standard':
            self.scaler = StandardScaler()
            df_scaled[self.numeric_columns] = self.scaler.fit_transform(df_scaled[self.numeric_columns])
            self.logger.info("Standardized numeric features")
        
        elif method == 'minmax':
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            df_scaled[self.numeric_columns] = scaler.fit_transform(df_scaled[self.numeric_columns])
            self.logger.info("Min-max scaled numeric features")
        
        return df_scaled
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new features through feature engineering"""
        df_features = df.copy()
        
        # Example feature engineering for fashion data
        # Add your specific feature engineering logic here
        
        # Example: Create body type features
        if 'chest_cm' in df_features.columns and 'waist_cm' in df_features.columns:
            df_features['chest_waist_ratio'] = df_features['chest_cm'] / df_features['waist_cm']
            self.logger.info("Created chest-waist ratio feature")
        
        if 'height_cm' in df_features.columns and 'weight_kg' in df_features.columns:
            df_features['bmi'] = df_features['weight_kg'] / ((df_features['height_cm'] / 100) ** 2)
            self.logger.info("Created BMI feature")
        
        # Example: Create size category features (commented out to avoid conflicts)
        # if 'chest_cm' in df_features.columns:
        #     df_features['size_category'] = pd.cut(
        #         df_features['chest_cm'],
        #         bins=[0, 90, 100, 110, 120, 200],
        #         labels=['XS', 'S', 'M', 'L', 'XL']
        #     )
        #     self.logger.info("Created size category feature")
        
        return df_features
    
    def remove_outliers(self, df: pd.DataFrame, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """Remove outliers from numeric columns"""
        df_clean = df.copy()
        initial_rows = len(df_clean)
        
        if method == 'iqr':
            for col in self.numeric_columns:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
        
        elif method == 'zscore':
            for col in self.numeric_columns:
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                df_clean = df_clean[z_scores < threshold]
        
        removed_rows = initial_rows - len(df_clean)
        self.logger.info(f"Removed {removed_rows} outlier rows")
        
        return df_clean
    
    def create_preprocessing_pipeline(self) -> Pipeline:
        """Create a complete preprocessing pipeline"""
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_columns),
                ('cat', categorical_transformer, self.categorical_columns)
            ],
            remainder='passthrough'
        )
        
        self.preprocessor = preprocessor
        self.logger.info("Created preprocessing pipeline")
        return preprocessor
    
    def preprocess_data(self, df: pd.DataFrame, target_column: str = None) -> Tuple[pd.DataFrame, pd.Series]:
        """Complete data preprocessing pipeline"""
        self.logger.info("Starting data preprocessing...")
        
        # Store target column
        if target_column and target_column in df.columns:
            self.target_column = target_column
            y = df[target_column]
            X = df.drop(columns=[target_column])
            
            # Convert target to string if it's categorical
            if y.dtype.name == 'category':
                y = y.astype(str)
        else:
            X = df
            y = None
        
        # Identify column types
        self.identify_column_types(X)
        
        # Handle missing values
        X = self.handle_missing_values(X)
        
        # Remove outliers
        X = self.remove_outliers(X)
        
        # Encode categorical variables
        X = self.encode_categorical_variables(X)
        
        # Scale numeric features
        X = self.scale_numeric_features(X)
        
        # Create new features
        X = self.create_features(X)
        
        # Final cleaning - handle categorical columns properly
        for col in X.columns:
            if X[col].dtype.name == 'category':
                # For categorical columns, fill with mode instead of 0
                if X[col].isnull().sum() > 0:
                    X[col] = X[col].fillna(X[col].mode()[0])
            else:
                # For numeric columns, fill with 0
                if X[col].isnull().sum() > 0:
                    X[col] = X[col].fillna(0)
        
        self.logger.info(f"Preprocessing complete. Final shape: {X.shape}")
        
        return X, y
    
    def save_preprocessor(self, filepath: str):
        """Save the fitted preprocessor"""
        import joblib
        joblib.dump(self.preprocessor, filepath)
        self.logger.info(f"Preprocessor saved to: {filepath}")
    
    def load_preprocessor(self, filepath: str):
        """Load a saved preprocessor"""
        import joblib
        self.preprocessor = joblib.load(filepath)
        self.logger.info(f"Preprocessor loaded from: {filepath}")

# Example usage
if __name__ == "__main__":
    # Test the preprocessor
    preprocessor = DataPreprocessor()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'chest_cm': [95, 100, 105, 110, 115],
        'waist_cm': [80, 85, 90, 95, 100],
        'height_cm': [170, 175, 180, 185, 190],
        'weight_kg': [70, 75, 80, 85, 90],
        'style': ['casual', 'formal', 'casual', 'formal', 'casual'],
        'size': ['M', 'L', 'L', 'XL', 'XL']
    })
    
    print("Original data:")
    print(sample_data)
    
    # Preprocess data
    X, y = preprocessor.preprocess_data(sample_data, target_column='size')
    
    print("\nPreprocessed data:")
    print(X.head())
