/**
 * API module for traffic prediction data
 * Handles fetching from FastAPI backend with automatic mock fallback
 */

// Mock data imports for fallback
import traffic15 from './mock/traffic_15.json';
import traffic30 from './mock/traffic_30.json';
import traffic60 from './mock/traffic_60.json';

// Mock data mapping by prediction minutes
const MOCK_DATA = {
    15: traffic15,
    30: traffic30,
    60: traffic60
};

/**
 * Calculate bounding box from Leaflet map bounds
 * @param {Object} bounds - Leaflet LatLngBounds object
 * @returns {string} - Comma-separated bbox string: west,south,east,north
 */
export function getBboxFromBounds(bounds) {
    const west = bounds.getWest().toFixed(4);
    const south = bounds.getSouth().toFixed(4);
    const east = bounds.getEast().toFixed(4);
    const north = bounds.getNorth().toFixed(4);
    return `${west},${south},${east},${north}`;
}

/**
 * Fetch traffic prediction data from API
 * Falls back to mock data if API is unavailable
 * 
 * @param {number} minutes - Prediction time: 15, 30, or 60
 * @param {string} bbox - Bounding box string (west,south,east,north)
 * @returns {Promise<Object>} - GeoJSON FeatureCollection
 */
export async function fetchTrafficPrediction(minutes, bbox) {
    const validMinutes = [15, 30, 60];
    if (!validMinutes.includes(minutes)) {
        console.warn(`Invalid minutes value: ${minutes}, defaulting to 15`);
        minutes = 15;
    }

    try {
        // Attempt to fetch from FastAPI backend
        const response = await fetch(
            `/api/traffic/predict?minutes=${minutes}&bbox=${bbox}`,
            {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                // Timeout after 5 seconds
                signal: AbortSignal.timeout(5000)
            }
        );

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();
        return { data, isMock: false };
    } catch (error) {
        // Log error and fallback to mock data
        console.warn('API unavailable, using mock data:', error.message);
        return { data: MOCK_DATA[minutes], isMock: true };
    }
}

/**
 * Search addresses using Nominatim (OpenStreetMap)
 * @param {string} query - Search query
 * @returns {Promise<Array>} - Array of search results
 */
export async function searchAddress(query) {
    if (!query || query.trim().length < 2) {
        return [];
    }

    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?` +
            `q=${encodeURIComponent(query)}&` +
            `format=json&` +
            `addressdetails=1&` +
            `limit=5&` +
            `countrycodes=kg&` +  // Restrict to Kyrgyzstan
            `viewbox=74.40,42.95,74.75,42.75&` +  // Bishkek viewport
            `bounded=0`,
            {
                headers: {
                    'Accept': 'application/json',
                    'User-Agent': 'BishkekTrafficPredictor/1.0'
                }
            }
        );

        if (!response.ok) {
            throw new Error(`Nominatim returned ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Address search failed:', error);
        return [];
    }
}
