import React, { useState, useEffect } from 'react';
import { Sparkles, ShoppingBag, Heart, ArrowRight, CheckCircle, AlertCircle, User, Ruler } from 'lucide-react';
import ApiService from '../services/api';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [measurementData, setMeasurementData] = useState(null);
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    loadMeasurementDataAndRecommendations();
  }, []);

  const loadMeasurementDataAndRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get measurement data from URL
      const urlParams = new URLSearchParams(window.location.search);
      const dataParam = urlParams.get('data');
      
      if (!dataParam) {
        // If no measurement data, redirect to measure page
        window.location.href = '/measure';
        return;
      }
      
      // Parse the measurement data
      const data = JSON.parse(decodeURIComponent(dataParam));
      setMeasurementData(data);
      
      console.log('📊 Measurement data received:', data);
      
      // Load recommendations based on measured size
      const recData = await ApiService.getRecommendations(data.size, data.gender, 20);
      setRecommendations(recData.recommendations || []);
      
      // Load statistics
      const statsData = await ApiService.getStatistics();
      setStatistics(statsData);
      
      console.log(`🎯 Loaded ${recData.recommendations?.length || 0} recommendations for size ${data.size}`);
      
    } catch (error) {
      console.error('Error loading data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return '/placeholder-clothing.svg';
    
    // Convert relative path to absolute URL for ML images
    if (imagePath.startsWith('data/images/')) {
      const imageUrl = `http://localhost:5001/${imagePath}`;
      console.log(`🖼️ Loading image: ${imageUrl}`);
      return imageUrl;
    }
    
    return imagePath;
  };

  const handleImageError = (e, item) => {
    console.log(`Image failed to load for item ${item.id}: ${item.image_path}`);
    e.target.src = '/placeholder-clothing.svg';
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceText = (score) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading your personalized recommendations...</h2>
          <p className="text-gray-500 mt-2">Based on your measurements</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 max-w-lg text-center shadow-xl">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Unable to Load Recommendations</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button 
            onClick={() => window.location.href = '/measure'}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-medium"
          >
            📏 Take Measurements Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      {/* Header with Measurement Summary */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Sparkles className="w-8 h-8 text-purple-600 mr-3" />
                AI Clothing Recommendations
              </h1>
              <p className="text-gray-600 mt-2">
                Personalized recommendations based on your measurements
              </p>
                              <div className="text-sm text-blue-600 mt-1 flex items-center">
                  <Ruler className="w-4 h-4 mr-1" />
                  Size System: Only L and XL available (L and XL recommended interchangeably)
                </div>
            </div>
            
            {statistics && (
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">
                  {statistics.total_upper_body_products?.toLocaleString() || '0'}
                </div>
                <div className="text-sm text-gray-500">Products Available</div>
                <div className="text-xs text-blue-500 mt-1">
                  Sizes: L (most common) • XL
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Measurement Summary Card */}
      {measurementData && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">Your Measurements</h2>
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold">{measurementData.measurements.chestCm?.toFixed(1)}</div>
                    <div className="text-sm opacity-90">Chest (cm)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold">{measurementData.measurements.shoulderCm?.toFixed(1)}</div>
                    <div className="text-sm opacity-90">Shoulder (cm)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold">{measurementData.measurements.upperWaistCm?.toFixed(1)}</div>
                    <div className="text-sm opacity-90">Waist (cm)</div>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm opacity-90 mb-2">Recommended Size</div>
                <div className="text-5xl font-bold">{measurementData.size}</div>
                <div className="text-sm opacity-90">{measurementData.gender}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Recommendations for Size {measurementData?.size}
          </h2>
          <span className="text-gray-600">
            {recommendations.length} products found based on your measurements
          </span>
          <div className="text-sm text-blue-600 mt-2 flex items-center">
            <CheckCircle className="w-4 h-4 mr-1" />
            Showing {measurementData?.size} products (L and XL products recommended interchangeably)
          </div>
        </div>

        {recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recommendations.map((item, index) => (
              <div key={`${item.id}-${index}`} className="bg-white rounded-xl shadow-sm border overflow-hidden hover:shadow-lg transition-shadow">
                {/* Product Image */}
                <div className="aspect-square bg-gray-100 relative">
                  {item.image_exists ? (
                    <img
                      src={getImageUrl(item.image_path)}
                      alt={item.product_name}
                      className="w-full h-full object-cover"
                      onError={(e) => handleImageError(e, item)}
                      onLoad={() => console.log(`Image loaded successfully for item ${item.id}`)}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <img src="/placeholder-clothing.svg" alt="No image available" className="w-24 h-24 opacity-50" />
                    </div>
                  )}
                  
                  {/* Confidence Badge */}
                  <div className="absolute top-2 right-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full bg-white shadow-sm ${getConfidenceColor(item.confidence_score)}`}>
                      {getConfidenceText(item.confidence_score)} Confidence
                    </span>
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                    {item.product_name}
                  </h3>
                  
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center justify-between">
                      <span>Type:</span>
                      <span className="font-medium capitalize">{item.article_type}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>Color:</span>
                      <span className="font-medium capitalize">{item.color}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>Usage:</span>
                      <span className="font-medium capitalize">{item.usage}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>Season:</span>
                      <span className="font-medium capitalize">{item.season}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="mt-4 flex items-center justify-between">
                    <button className="flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View Details
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </button>
                    
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                        <Heart className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-blue-500 transition-colors">
                        <ShoppingBag className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <ShoppingBag className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
            <p className="text-gray-600">
              Try taking measurements again or adjusting your preferences
            </p>
            <button 
              onClick={() => window.location.href = '/measure'}
              className="mt-4 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-medium"
            >
              📏 Retake Measurements
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;
