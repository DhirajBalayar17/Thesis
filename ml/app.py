from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import yaml
import os
from pathlib import Path

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from services.upper_body_recommender import UpperBodyRecommender

# Load configuration
def load_config():
    config_path = "config/config.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

config = load_config()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize recommender
recommender = None
try:
    recommender = UpperBodyRecommender(config)
    logger.info("✅ Upper-body recommender initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing recommender: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Fashion AI ML API",
        "recommender_ready": recommender is not None
    })

@app.route('/data/images/<filename>', methods=['GET'])
def serve_image(filename):
    """Serve product images"""
    try:
        # Get the data directory path from config
        data_dir = config.get('data_path', 'data')
        images_dir = os.path.join(data_dir, 'images')
        
        # Check if file exists
        file_path = os.path.join(images_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "Image not found"}), 404
        
        # Serve the image file
        return send_from_directory(images_dir, filename)
        
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return jsonify({"error": "Error serving image"}), 500

@app.route('/api/recommendations/upper-body', methods=['POST'])
def get_upper_body_recommendations():
    """Get upper-body clothing recommendations based on user size"""
    try:
        if not recommender:
            return jsonify({"error": "Recommender not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_size = data.get('size')
        if not user_size:
            return jsonify({"error": "Size parameter is required"}), 400
        
        gender = data.get('gender', 'Men')
        max_recommendations = data.get('max_recommendations', 10)
        include_images_only = data.get('include_images_only', True)
        
        # Get recommendations
        result = recommender.get_upper_body_recommendations(
            user_size=user_size,
            max_recommendations=max_recommendations,
            gender=gender,
            include_images_only=include_images_only
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in upper-body recommendations: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations/search', methods=['POST'])
def search_products():
    """Search products by query and size"""
    try:
        if not recommender:
            return jsonify({"error": "Recommender not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        query = data.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        user_size = data.get('size')
        max_results = data.get('max_results', 20)
        
        # Search products
        results = recommender.search_products(
            query=query,
            user_size=user_size,
            max_results=max_results
        )
        
        return jsonify({
            "query": query,
            "size": user_size,
            "results": results,
            "total_results": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in product search: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get dataset statistics"""
    try:
        if not recommender:
            return jsonify({"error": "Recommender not initialized"}), 500
        
        stats = recommender.get_size_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sizes', methods=['GET'])
def get_available_sizes():
    """Get list of available sizes"""
    try:
        if not recommender:
            return jsonify({"error": "Recommender not initialized"}), 500
        
        stats = recommender.get_size_statistics()
        sizes = list(stats.get('size_distribution', {}).keys())
        
        return jsonify({
            "available_sizes": sizes,
            "total_sizes": len(sizes)
        })
        
    except Exception as e:
        logger.error(f"Error getting sizes: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint"""
    return jsonify({
        "status": "running",
        "service": "Fashion AI ML API",
        "endpoints": [
            "/health",
            "/api/recommendations/upper-body",
            "/api/recommendations/search", 
            "/api/statistics",
            "/api/sizes"
        ]
    })

if __name__ == '__main__':
    port = config.get('api', {}).get('port', 5001)
    host = config.get('api', {}).get('host', '0.0.0.0')
    debug = config.get('api', {}).get('debug', False)
    
    logger.info(f"🚀 Starting Fashion AI ML API on {host}:{port}")
    logger.info(f"📊 Upper-body recommender: {'✅ Ready' if recommender else '❌ Failed'}")
    
    app.run(host=host, port=port, debug=debug)
