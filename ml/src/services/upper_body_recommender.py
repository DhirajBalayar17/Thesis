import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path

class UpperBodyRecommender:
    """
    Upper-body clothing recommendation service
    Matches user size to products and links to images
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.styles_df = None
        self.images_dir = "data/images"
        self.styles_file = "data/styles.csv"
        self.upper_body_types = {
            'Tshirts', 'Shirts', 'Jackets', 'Hoodies', 'Sweatshirts', 
            'Blazers', 'Sweaters', 'Kurta', 'Topwear'
        }
        self.load_data()
        
    def load_data(self):
        """Load styles data and validate images"""
        try:
            # Load styles CSV
            self.styles_df = pd.read_csv(self.styles_file)
            self.logger.info(f"Loaded styles data: {len(self.styles_df)} products")
            
            # Validate image existence
            self._validate_images()
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            self.styles_df = pd.DataFrame()
    
    def _validate_images(self):
        """Validate which products have corresponding images"""
        try:
            available_images = set()
            if os.path.exists(self.images_dir):
                for file in os.listdir(self.images_dir):
                    if file.endswith('.jpg') or file.endswith('.png'):
                        # Extract ID from filename (remove extension)
                        img_id = file.split('.')[0]
                        available_images.add(img_id)
            
            # Add image_exists column to dataframe
            self.styles_df['image_exists'] = self.styles_df['id'].astype(str).isin(available_images)
            
            total_products = len(self.styles_df)
            products_with_images = self.styles_df['image_exists'].sum()
            
            self.logger.info(f"Image validation complete:")
            self.logger.info(f"  - Total products: {total_products}")
            self.logger.info(f"  - Products with images: {products_with_images}")
            self.logger.info(f"  - Image coverage: {products_with_images/total_products*100:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error validating images: {e}")
    
    def get_upper_body_recommendations(
        self, 
        user_size: str,
        max_recommendations: int = 10,
        gender: str = "Men",
        include_images_only: bool = True
    ) -> Dict:
        """
        Get upper-body clothing recommendations based on user size
        
        Args:
            user_size: User's size (XXS, XS, S, M, L, XL, XXL)
            max_recommendations: Maximum number of recommendations
            gender: Gender filter (Men, Women, Unisex)
            include_images_only: Only return products with images
            
        Returns:
            Dict with recommendations and metadata
        """
        try:
            # Validate user size - only L and XL are supported
            valid_sizes = {'L', 'XL'}
            if user_size not in valid_sizes:
                # Auto-correct to L if invalid size provided
                user_size = 'L'
                self.logger.info(f"Size '{user_size}' not supported, defaulting to L")
            
            # Ensure we're working with valid sizes only
            if user_size not in valid_sizes:
                return {
                    "error": f"Only L and XL sizes are supported. Defaulting to L.",
                    "recommendations": [],
                    "accuracy_score": 0.0
                }
            
            # Filter products
            filtered_df = self._filter_products(user_size, gender, include_images_only)
            
            if filtered_df.empty:
                return {
                    "message": f"No upper-body products found for size '{user_size}' and gender '{gender}'",
                    "recommendations": [],
                    "accuracy_score": 0.0
                }
            
            # Get recommendations
            recommendations = self._format_recommendations(filtered_df, max_recommendations)
            
            # Calculate accuracy score
            accuracy_score = self._calculate_accuracy_score(filtered_df, user_size)
            
            # Prepare response
            response = {
                "user_size": user_size,
                "gender": gender,
                "total_products_found": len(filtered_df),
                "recommendations_returned": len(recommendations),
                "accuracy_score": accuracy_score,
                "recommendations": recommendations,
                "metadata": {
                    "upper_body_types": list(self.upper_body_types),
                    "image_coverage": self.styles_df['image_exists'].sum() / len(self.styles_df),
                    "total_dataset_size": len(self.styles_df)
                }
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return {
                "error": f"Error processing request: {str(e)}",
                "recommendations": [],
                "accuracy_score": 0.0
            }
    
    def _filter_products(self, user_size: str, gender: str, include_images_only: bool) -> pd.DataFrame:
        """Filter products based on criteria"""
        try:
            # Start with all products
            filtered = self.styles_df.copy()
            
            # Filter by size - only allow L and XL sizes
            valid_sizes = {'L', 'XL'}
            if user_size not in valid_sizes:
                # If user size is not L or XL, default to L (more common)
                user_size = 'L'
            
            filtered = filtered[filtered['size'] == user_size]
            
            # Filter by gender
            if gender != "All":
                filtered = filtered[filtered['gender'] == gender]
            
            # Filter by upper-body article types
            filtered = filtered[filtered['articleType'].isin(self.upper_body_types)]
            
            # Filter by image existence if requested
            if include_images_only:
                filtered = filtered[filtered['image_exists'] == True]
            
            # Sort by relevance with L and XL priority (L products first, then XL)
            # This ensures L and XL get equal priority
            filtered['size_priority'] = filtered['size'].map({'L': 1, 'XL': 1})
            filtered = filtered.sort_values(['size_priority', 'masterCategory', 'subCategory', 'articleType'])
            
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error filtering products: {e}")
            return pd.DataFrame()
    
    def _format_recommendations(self, df: pd.DataFrame, max_recommendations: int) -> List[Dict]:
        """Format recommendations with image paths"""
        try:
            recommendations = []
            
            for _, row in df.head(max_recommendations).iterrows():
                # Check if image exists
                img_id = str(row['id'])
                image_path = f"{self.images_dir}/{img_id}.jpg"
                
                # Verify image file exists
                if not os.path.exists(image_path):
                    # Try PNG format
                    image_path = f"{self.images_dir}/{img_id}.png"
                    if not os.path.exists(image_path):
                        image_path = None
                
                recommendation = {
                    "id": str(row['id']),
                    "product_name": row.get('productDisplayName', 'N/A'),
                    "article_type": row.get('articleType', 'N/A'),
                    "category": row.get('subCategory', 'N/A'),
                    "master_category": row.get('masterCategory', 'N/A'),
                    "color": row.get('baseColour', 'N/A'),
                    "season": row.get('season', 'N/A'),
                    "year": row.get('year', 'N/A'),
                    "usage": row.get('usage', 'N/A'),
                    "gender": row.get('gender', 'N/A'),
                    "size": row.get('size', 'N/A'),
                    "image_path": image_path,
                    "image_exists": image_path is not None,
                    "confidence_score": self._calculate_product_confidence(row)
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error formatting recommendations: {e}")
            return []
    
    def _calculate_product_confidence(self, row: pd.Series) -> float:
        """Calculate confidence score for a product"""
        try:
            confidence = 0.0
            
            # Base confidence for having image
            if row.get('image_exists', False):
                confidence += 0.3
            
            # Confidence for complete product information
            required_fields = ['productDisplayName', 'articleType', 'baseColour', 'usage']
            complete_info = sum(1 for field in required_fields if pd.notna(row.get(field, '')))
            confidence += (complete_info / len(required_fields)) * 0.4
            
            # Confidence for specific article types (prioritize main types)
            main_types = {'Tshirts', 'Shirts', 'Jackets'}
            if row.get('articleType') in main_types:
                confidence += 0.2
            
            # Confidence for recent products
            try:
                year = int(row.get('year', 0))
                if 2015 <= year <= 2024:
                    confidence += 0.1
            except:
                pass
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _calculate_accuracy_score(self, filtered_df: pd.DataFrame, user_size: str) -> float:
        """Calculate overall accuracy score for recommendations"""
        try:
            if filtered_df.empty:
                return 0.0
            
            # Base accuracy from having products
            base_accuracy = 0.6
            
            # Accuracy from image coverage
            image_coverage = filtered_df['image_exists'].sum() / len(filtered_df)
            image_accuracy = image_coverage * 0.3
            
            # Accuracy from data completeness
            completeness_score = 0.0
            required_fields = ['productDisplayName', 'articleType', 'baseColour', 'usage']
            for field in required_fields:
                if field in filtered_df.columns:
                    completeness_score += (filtered_df[field].notna().sum() / len(filtered_df))
            completeness_accuracy = (completeness_score / len(required_fields)) * 0.1
            
            total_accuracy = base_accuracy + image_accuracy + completeness_accuracy
            
            return min(total_accuracy, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating accuracy: {e}")
            return 0.5
    
    def get_size_statistics(self) -> Dict:
        """Get statistics about available sizes"""
        try:
            if self.styles_df is None or self.styles_df.empty:
                return {}
            
            # Filter upper-body items only
            upper_body_df = self.styles_df[self.styles_df['articleType'].isin(self.upper_body_types)]
            
            # Filter to only L and XL sizes
            valid_sizes = {'L', 'XL'}
            upper_body_df = upper_body_df[upper_body_df['size'].isin(valid_sizes)]
            
            # Size distribution (only L and XL)
            size_counts = upper_body_df['size'].value_counts().to_dict()
            
            # Gender distribution for upper-body items
            gender_counts = upper_body_df['gender'].value_counts().to_dict()
            
            # Article type distribution
            article_counts = upper_body_df['articleType'].value_counts().to_dict()
            
            # Image coverage by size (only L and XL)
            image_coverage_by_size = {}
            for size in valid_sizes:
                size_df = upper_body_df[upper_body_df['size'] == size]
                if len(size_df) > 0:
                    coverage = size_df['image_exists'].sum() / len(size_df)
                    image_coverage_by_size[size] = coverage
                else:
                    image_coverage_by_size[size] = 0.0
            
            return {
                "total_upper_body_products": len(upper_body_df),
                "size_distribution": size_counts,
                "gender_distribution": gender_counts,
                "article_type_distribution": article_counts,
                "image_coverage_by_size": image_coverage_by_size,
                "supported_sizes": list(valid_sizes),
                "size_priority": "L and XL (equal priority)"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting size statistics: {e}")
            return {}
    
    def search_products(self, query: str, user_size: str = None, max_results: int = 20) -> List[Dict]:
        """Search products by text query"""
        try:
            if self.styles_df is None or self.styles_df.empty:
                return []
            
            # Filter by size if specified (only L and XL allowed)
            search_df = self.styles_df.copy()
            if user_size:
                # Validate size - only L and XL supported
                if user_size not in {'L', 'XL'}:
                    user_size = 'L'  # Default to L
                search_df = search_df[search_df['size'] == user_size]
            else:
                # If no size specified, only show L and XL products
                search_df = search_df[search_df['size'].isin({'L', 'XL'})]
            
            # Filter upper-body items
            search_df = search_df[search_df['articleType'].isin(self.upper_body_types)]
            
            # Text search in product name and description
            query_lower = query.lower()
            mask = (
                search_df['productDisplayName'].str.lower().str.contains(query_lower, na=False) |
                search_df['articleType'].str.lower().str.contains(query_lower, na=False) |
                search_df['baseColour'].str.lower().str.contains(query_lower, na=False)
            )
            
            search_df = search_df[mask]
            
            # Sort with L and XL equal priority
            search_df['size_priority'] = search_df['size'].map({'L': 1, 'XL': 1})
            search_df = search_df.sort_values(['size_priority', 'masterCategory', 'subCategory', 'articleType'])
            
            # Format results
            results = self._format_recommendations(search_df, max_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching products: {e}")
            return []
