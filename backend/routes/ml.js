const express = require('express');
const axios = require('axios');
const router = express.Router();

// ML API configuration
const ML_API_BASE_URL = 'http://localhost:5001';

// Health check for ML API
router.get('/health', async (req, res) => {
    try {
        const response = await axios.get(`${ML_API_BASE_URL}/health`);
        res.json({
            status: 'connected',
            ml_api: response.data,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'disconnected',
            error: 'ML API not available',
            details: error.message
        });
    }
});

// Get ML API status
router.get('/status', async (req, res) => {
    try {
        const response = await axios.get(`${ML_API_BASE_URL}/status`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({
            error: 'Failed to get ML API status',
            details: error.message
        });
    }
});

// Get upper-body clothing recommendations
router.post('/recommendations/upper-body', async (req, res) => {
    try {
        const { size, gender, max_recommendations } = req.body;
        
        if (!size) {
            return res.status(400).json({
                error: 'Size parameter is required'
            });
        }
        
        const requestData = {
            size: size,
            gender: gender || 'Men',
            max_recommendations: max_recommendations || 10,
            include_images_only: true
        };
        
        const response = await axios.post(`${ML_API_BASE_URL}/api/recommendations/upper-body`, requestData);
        res.json(response.data);
        
    } catch (error) {
        res.status(500).json({
            error: 'Failed to get recommendations',
            details: error.message
        });
    }
});

// Search products
router.post('/recommendations/search', async (req, res) => {
    try {
        const { query, size, max_results } = req.body;
        
        if (!query) {
            return res.status(400).json({
                error: 'Query parameter is required'
            });
        }
        
        const requestData = {
            query: query,
            size: size,
            max_results: max_results || 20
        };
        
        const response = await axios.post(`${ML_API_BASE_URL}/api/recommendations/search`, requestData);
        res.json(response.data);
        
    } catch (error) {
        res.status(500).json({
            error: 'Failed to search products',
            details: error.message
        });
    }
});

// Get dataset statistics
router.get('/statistics', async (req, res) => {
    try {
        const response = await axios.get(`${ML_API_BASE_URL}/api/statistics`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({
            error: 'Failed to get statistics',
            details: error.message
        });
    }
});

// Get available sizes
router.get('/sizes', async (req, res) => {
    try {
        const response = await axios.get(`${ML_API_BASE_URL}/api/sizes`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({
            error: 'Failed to get available sizes',
            details: error.message
        });
    }
});



// Legacy endpoint for backward compatibility
router.post('/predict', async (req, res) => {
    try {
        const { measurements } = req.body;
        
        if (!measurements) {
            return res.status(400).json({
                error: 'Measurements data is required'
            });
        }
        
        // For now, redirect to size-based recommendations
        // You can implement measurement-to-size conversion later
        const estimatedSize = estimateSizeFromMeasurements(measurements);
        
        const requestData = {
            size: estimatedSize,
            gender: 'Men',
            max_recommendations: 10,
            include_images_only: true
        };
        
        const response = await axios.post(`${ML_API_BASE_URL}/api/recommendations/upper-body`, requestData);
        res.json({
            ...response.data,
            estimated_size: estimatedSize,
            note: 'Size estimated from measurements'
        });
        
    } catch (error) {
        res.status(500).json({
            error: 'Prediction failed',
            details: error.message
        });
    }
});

// Helper function to estimate size from measurements (improved)
function estimateSizeFromMeasurements(measurements, gender = 'Men') {
    const chestCm = measurements.chestCm;
    const waistCm = measurements.upperWaistCm || measurements.waistCm;
    const shoulderCm = measurements.shoulderCm;
    
    if (!chestCm || !waistCm || !shoulderCm || chestCm <= 0 || waistCm <= 0 || shoulderCm <= 0) {
        return 'M'; // Default fallback if measurements are missing
    }
    
    // More sophisticated sizing algorithm that considers individual measurements
    // This ensures even small differences in measurements result in different sizes
    
    // Primary size based on chest (most important for tops)
    // Using realistic size ranges based on actual human measurements
    let primarySize = 'M';
    if (chestCm < 80) primarySize = 'XXS';      // Very small frame
    else if (chestCm < 85) primarySize = 'XS';   // Small frame
    else if (chestCm < 90) primarySize = 'S';    // Small-medium frame
    else if (chestCm < 95) primarySize = 'M';    // Medium frame (most common)
    else if (chestCm < 100) primarySize = 'L';   // Large frame
    else if (chestCm < 105) primarySize = 'XL';  // Extra large frame
    else if (chestCm < 110) primarySize = 'XXL'; // 2X large frame
    else if (chestCm < 115) primarySize = '3XL'; // 3X large frame
    else primarySize = '4XL';                    // 4X large frame
    
    // Secondary adjustment based on waist-to-chest ratio
    const waistChestRatio = waistCm / chestCm;
    let sizeAdjustment = 0;
    
    if (waistChestRatio < 0.80) {
        // Very slim build - go down one size
        sizeAdjustment = -1;
    } else if (waistChestRatio > 0.90) {
        // Fuller build - go up one size
        sizeAdjustment = 1;
    }
    
    // Tertiary adjustment based on shoulder-to-chest ratio
    const shoulderChestRatio = shoulderCm / chestCm;
    if (shoulderChestRatio > 0.60) {
        // Very broad shoulders - go up one size
        sizeAdjustment += 1;
    } else if (shoulderChestRatio < 0.50) {
        // Very narrow shoulders - go down one size
        sizeAdjustment -= 1;
    }
    
    // Apply size adjustments
    const sizeOrder = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', '4XL'];
    const currentIndex = sizeOrder.indexOf(primarySize);
    const adjustedIndex = Math.max(0, Math.min(sizeOrder.length - 1, currentIndex + sizeAdjustment));
    
    const finalSize = sizeOrder[adjustedIndex];
    
    // Log the calculation for debugging
    console.log(`Backend Size Calculation:`, {
        chestCm,
        waistCm, 
        shoulderCm,
        primarySize,
        waistChestRatio: waistChestRatio.toFixed(3),
        shoulderChestRatio: shoulderChestRatio.toFixed(3),
        sizeAdjustment,
        finalSize
    });
    
    return finalSize;
}

module.exports = router;
