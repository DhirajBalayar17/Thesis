import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional
import logging

class ClothingRecommender:
    """
    Clothing recommendation service for upper body clothing (shirts, t-shirts)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.image_index = None
        self.clothing_database = None
        self.load_image_index()
        
    def load_image_index(self):
        """Load the image index file"""
        try:
            image_index_path = self.config['data']['image_index']
            if os.path.exists(image_index_path):
                self.image_index = pd.read_csv(image_index_path)
                self.logger.info(f"Loaded image index with {len(self.image_index)} items")
            else:
                self.logger.warning(f"Image index not found at {image_index_path}")
                self.image_index = pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error loading image index: {e}")
            self.image_index = pd.DataFrame()
    
    def get_clothing_recommendations(
        self, 
        measurements: Dict, 
        max_recommendations: int = 5,
        include_images: bool = True
    ) -> List[Dict]:
        """
        Get clothing recommendations based on body measurements
        
        Args:
            measurements: Dict with body measurements
            max_recommendations: Maximum number of recommendations
            include_images: Whether to include image paths
            
        Returns:
            List of clothing recommendations
        """
        try:
            # Extract key measurements
            chest_cm = measurements.get('chest_cm')
            waist_cm = measurements.get('waist_cm')
            height_cm = measurements.get('height_cm')
            weight_kg = measurements.get('weight_kg')
            age = measurements.get('age', 25)
            shoulder_cm = measurements.get('shoulder_cm')
            
            if not all([chest_cm, waist_cm, height_cm, weight_kg]):
                raise ValueError("Missing required measurements")
            
            # Calculate body type and style preferences
            body_type = self._calculate_body_type(chest_cm, waist_cm, height_cm, weight_kg)
            style_preference = self._calculate_style_preference(age, measurements)
            
            # Get size recommendation
            recommended_size = self._get_size_recommendation(chest_cm, shoulder_cm)
            
            # Filter clothing based on recommendations
            recommendations = self._filter_clothing(
                size=recommended_size,
                body_type=body_type,
                style_preference=style_preference,
                max_recommendations=max_recommendations
            )
            
            # Add image paths if requested
            if include_images and self.image_index is not None:
                recommendations = self._add_image_paths(recommendations)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return []
    
    def _calculate_body_type(self, chest_cm: float, waist_cm: float, height_cm: float, weight_kg: float) -> str:
        """Calculate body type based on measurements"""
        try:
            # Calculate BMI
            height_m = height_cm / 100
            bmi = weight_kg / (height_m ** 2)
            
            # Calculate chest-waist ratio
            chest_waist_ratio = chest_cm / waist_cm if waist_cm > 0 else 1
            
            if bmi < 18.5:
                return "slim"
            elif bmi < 25:
                if chest_waist_ratio > 1.2:
                    return "athletic"
                else:
                    return "regular"
            elif bmi < 30:
                return "regular"
            else:
                return "plus-size"
        except:
            return "regular"
    
    def _calculate_style_preference(self, age: int, measurements: Dict) -> str:
        """Calculate style preference based on age and measurements"""
        try:
            if age < 25:
                return "trendy"
            elif age < 35:
                return "modern"
            elif age < 50:
                return "classic"
            else:
                return "conservative"
        except:
            return "modern"
    
    def _get_size_recommendation(self, chest_cm: float, shoulder_cm: float) -> str:
        """Get size recommendation based on chest measurement"""
        try:
            if chest_cm < 86:
                return "XS"
            elif chest_cm < 94:
                return "S"
            elif chest_cm < 102:
                return "M"
            elif chest_cm < 110:
                return "L"
            elif chest_cm < 118:
                return "XL"
            else:
                return "XXL"
        except:
            return "M"
    
    def _filter_clothing(
        self, 
        size: str, 
        body_type: str, 
        style_preference: str,
        max_recommendations: int
    ) -> List[Dict]:
        """Filter clothing based on recommendations"""
        try:
            # This would typically query a clothing database
            # For now, return sample recommendations
            sample_recommendations = [
                {
                    "id": "001",
                    "name": "Classic Blue Shirt",
                    "type": "shirt",
                    "size": size,
                    "style": "casual",
                    "fit": "regular",
                    "body_type": body_type,
                    "style_preference": style_preference,
                    "description": f"Perfect {size} size {body_type} fit shirt",
                    "price_range": "medium"
                },
                {
                    "id": "002", 
                    "name": "Modern White T-shirt",
                    "type": "tshirt",
                    "size": size,
                    "style": "casual",
                    "fit": "slim" if body_type == "slim" else "regular",
                    "body_type": body_type,
                    "style_preference": style_preference,
                    "description": f"Stylish {size} {body_type} t-shirt",
                    "price_range": "low"
                },
                {
                    "id": "003",
                    "name": "Formal Business Shirt",
                    "type": "shirt", 
                    "size": size,
                    "style": "formal",
                    "fit": "regular",
                    "body_type": body_type,
                    "style_preference": style_preference,
                    "description": f"Professional {size} {body_type} business shirt",
                    "price_range": "high"
                }
            ]
            
            return sample_recommendations[:max_recommendations]
            
        except Exception as e:
            self.logger.error(f"Error filtering clothing: {e}")
            return []
    
    def _add_image_paths(self, recommendations: List[Dict]) -> List[Dict]:
        """Add image paths to recommendations"""
        try:
            for rec in recommendations:
                if self.image_index is not None and not self.image_index.empty:
                    # Find matching image by ID
                    matching_images = self.image_index[self.image_index['id'] == rec['id']]
                    if not matching_images.empty:
                        rec['image_path'] = matching_images.iloc[0]['image_path']
                        rec['clothing_type'] = matching_images.iloc[0]['clothing_type']
                    else:
                        rec['image_path'] = f"default_{rec['type']}.jpg"
                        rec['clothing_type'] = rec['type']
                else:
                    rec['image_path'] = f"default_{rec['type']}.jpg"
                    rec['clothing_type'] = rec['type']
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error adding image paths: {e}")
            return recommendations
    
    def get_recommendation_summary(self, measurements: Dict) -> Dict:
        """Get a summary of recommendations"""
        try:
            recommendations = self.get_clothing_recommendations(measurements, max_recommendations=3)
            
            summary = {
                "recommended_size": self._get_size_recommendation(
                    measurements.get('chest_cm'), 
                    measurements.get('shoulder_cm')
                ),
                "body_type": self._calculate_body_type(
                    measurements.get('chest_cm'),
                    measurements.get('waist_cm'), 
                    measurements.get('height_cm'),
                    measurements.get('weight_kg')
                ),
                "style_preference": self._calculate_style_preference(
                    measurements.get('age', 25), 
                    measurements
                ),
                "recommendations_count": len(recommendations),
                "clothing_types": list(set([r['type'] for r in recommendations])),
                "fit_suggestions": list(set([r['fit'] for r in recommendations]))
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting recommendation summary: {e}")
            return {}
