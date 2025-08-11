// API service for communicating with the backend
const API_BASE_URL = 'http://localhost:5002/api';

class ApiService {
    // Get upper-body clothing recommendations
    static async getRecommendations(size, gender = 'Men', maxRecommendations = 10) {
        try {
            // Validate size - only L and XL are supported
            const validSizes = ['L', 'XL'];
            if (!validSizes.includes(size)) {
                console.warn(`Size '${size}' not supported, defaulting to L`);
                size = 'L'; // Default to L (most common)
            }
            
            const response = await fetch(`${API_BASE_URL}/ml/recommendations/upper-body`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    size,
                    gender,
                    max_recommendations: maxRecommendations
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            throw error;
        }
    }

    // Search products
    static async searchProducts(query, size = null, maxResults = 20) {
        try {
            // Validate size if provided - only L and XL are supported
            if (size) {
                const validSizes = ['L', 'XL'];
                if (!validSizes.includes(size)) {
                    console.warn(`Size '${size}' not supported, defaulting to L`);
                    size = 'L'; // Default to L (most common)
                }
            }
            
            const response = await fetch(`${API_BASE_URL}/ml/recommendations/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    size,
                    max_results: maxResults
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error searching products:', error);
            throw error;
        }
    }

    // Get available sizes
    static async getAvailableSizes() {
        try {
            const response = await fetch(`${API_BASE_URL}/ml/sizes`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching sizes:', error);
            throw error;
        }
    }

    // Get dataset statistics
    static async getStatistics() {
        try {
            const response = await fetch(`${API_BASE_URL}/ml/statistics`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching statistics:', error);
            throw error;
        }
    }

    // Check backend health
    static async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/ml/health`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    }
}

export default ApiService;
