import React, { useState, useCallback, useRef } from 'react';
import ControlPanel from './components/ControlPanel';
import MapView from './components/MapView';
import { ToastContainer } from './components/Toast';
import { fetchTrafficPrediction, getBboxFromBounds } from './api';

/**
 * Main App component
 * Manages application state and coordinates between components
 */
export default function App() {
    // State management
    const [selectedMinutes, setSelectedMinutes] = useState(15);
    const [trafficData, setTrafficData] = useState(null);
    const [searchLocation, setSearchLocation] = useState(null);
    const [userLocation, setUserLocation] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isLocating, setIsLocating] = useState(false);
    const [isMockData, setIsMockData] = useState(false);
    const [toasts, setToasts] = useState([]);

    // Map reference for accessing bounds
    const mapRef = useRef(null);

    /**
     * Add a toast notification
     */
    const addToast = useCallback((message, type = 'info') => {
        const id = Date.now() + Math.random();
        setToasts((prev) => [...prev, { id, message, type }]);
    }, []);

    /**
     * Remove a toast notification
     */
    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    /**
     * Handle map ready event
     */
    const handleMapReady = useCallback((map) => {
        mapRef.current = map;
    }, []);

    /**
     * Handle location selection from search
     */
    const handleLocationSelect = useCallback((location) => {
        setSearchLocation(location);
        addToast(`Найдено: ${location.name?.split(',')[0]}`, 'success');
    }, [addToast]);

    /**
     * Handle traffic prediction request
     * Fetches data from API with fallback to mock
     */
    const handlePredict = useCallback(async () => {
        if (!mapRef.current) {
            addToast('Карта ещё загружается...', 'warning');
            return;
        }

        setIsLoading(true);

        try {
            // Get current viewport bounding box
            const bounds = mapRef.current.getBounds();
            const bbox = getBboxFromBounds(bounds);

            // Fetch traffic prediction
            const { data, isMock } = await fetchTrafficPrediction(selectedMinutes, bbox);

            setTrafficData(data);
            setIsMockData(isMock);

            if (isMock) {
                addToast('API недоступен, показаны демо-данные', 'warning');
            } else {
                addToast(`Прогноз на ${selectedMinutes} минут загружен`, 'success');
            }
        } catch (error) {
            console.error('Prediction error:', error);
            addToast('Ошибка загрузки прогноза', 'error');
        } finally {
            setIsLoading(false);
        }
    }, [selectedMinutes, addToast]);

    /**
     * Handle geolocation request
     */
    const handleLocateMe = useCallback(() => {
        if (!navigator.geolocation) {
            addToast('Геолокация не поддерживается браузером', 'error');
            return;
        }

        setIsLocating(true);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                setUserLocation({ lat: latitude, lng: longitude });
                setIsLocating(false);
                addToast('Местоположение определено', 'success');
            },
            (error) => {
                setIsLocating(false);
                console.error('Geolocation error:', error);

                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        addToast('Доступ к геолокации запрещён', 'error');
                        break;
                    case error.POSITION_UNAVAILABLE:
                        addToast('Местоположение недоступно', 'error');
                        break;
                    case error.TIMEOUT:
                        addToast('Время ожидания геолокации истекло', 'error');
                        break;
                    default:
                        addToast('Ошибка определения местоположения', 'error');
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }, [addToast]);

    /**
     * Handle API/search errors
     */
    const handleError = useCallback((message) => {
        addToast(message, 'error');
    }, [addToast]);

    return (
        <div className="app-container">
            <h1>Hello Traffic Analysis</h1>
            {/* Control Panel */}
            <ControlPanel
                selectedMinutes={selectedMinutes}
                onMinutesChange={setSelectedMinutes}
                onPredict={handlePredict}
                onLocationSelect={handleLocationSelect}
                onError={handleError}
                isLoading={isLoading}
                isMockData={isMockData}
            />

            {/* Map View */}
            <MapView
                trafficData={trafficData}
                searchLocation={searchLocation}
                userLocation={userLocation}
                onMapReady={handleMapReady}
                onLocateMe={handleLocateMe}
                isLocating={isLocating}
            />

            {/* Toast Notifications */}
            <ToastContainer
                toasts={toasts}
                removeToast={removeToast}
            />
        </div>
    );
}
