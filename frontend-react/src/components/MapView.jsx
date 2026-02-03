import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Crosshair } from 'lucide-react';
import centralDistrict from '../mock/central_district.geojson';
import Legend from './Legend';

// Bishkek city center coordinates (pilot zone)
const BISHKEK_CENTER = [42.87, 74.59];
const DEFAULT_ZOOM = 14;

// Fix Leaflet default marker icon issue with bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom marker icon for search results
const searchMarkerIcon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// Custom marker for user location (blue)
const userLocationIcon = L.divIcon({
    className: 'user-location-marker',
    html: `<div style="
    width: 16px;
    height: 16px;
    background: #3b82f6;
    border: 3px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  "></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
});

/**
 * Get color based on congestion level
 * @param {number} congestion - Value between 0 and 1
 * @returns {string} - Hex color code
 */
function getCongestionColor(congestion) {
    if (congestion <= 0.33) return '#22c55e'; // Green - low
    if (congestion <= 0.66) return '#f59e0b'; // Orange - medium
    return '#ef4444'; // Red - high
}

/**
 * Get congestion level label
 * @param {number} congestion - Value between 0 and 1
 * @returns {string} - Level name
 */
function getCongestionLevel(congestion) {
    if (congestion <= 0.33) return 'low';
    if (congestion <= 0.66) return 'medium';
    return 'high';
}

/**
 * Component to handle map view changes (centering, etc.)
 */
function MapController({ center, searchLocation, userLocation }) {
    const map = useMap();

    useEffect(() => {
        if (searchLocation) {
            map.flyTo([searchLocation.lat, searchLocation.lng], 16, {
                duration: 1
            });
        }
    }, [searchLocation, map]);

    useEffect(() => {
        if (userLocation) {
            map.flyTo([userLocation.lat, userLocation.lng], 16, {
                duration: 1
            });
        }
    }, [userLocation, map]);

    return null;
}

/**
 * MapView component
 * Renders Leaflet map with traffic overlay, markers, and controls
 */
export default function MapView({
    trafficData,
    searchLocation,
    userLocation,
    onMapReady,
    onLocateMe,
    isLocating
}) {
    const mapRef = useRef(null);

    // Style function for traffic overlay GeoJSON
    const trafficStyle = (feature) => {
        const congestion = feature.properties?.congestion || 0;
        const isPolygon = feature.geometry?.type === 'Polygon';

        return {
            color: getCongestionColor(congestion),
            weight: isPolygon ? 2 : (congestion > 0.66 ? 6 : 5),
            opacity: 0.85,
            fillColor: getCongestionColor(congestion),
            fillOpacity: isPolygon ? 0.3 : 0
        };
    };

    // Style for central district boundary
    const districtStyle = {
        color: '#6366f1',
        weight: 2,
        opacity: 0.6,
        fillColor: '#6366f1',
        fillOpacity: 0.05,
        dashArray: '8, 4'
    };

    // Handle each traffic feature
    const onEachTrafficFeature = (feature, layer) => {
        const props = feature.properties || {};
        const congestion = props.congestion || 0;
        const congestionPercent = Math.round(congestion * 100);
        const level = getCongestionLevel(congestion);

        // Tooltip on hover
        layer.bindTooltip(`Загруженность: ${congestionPercent}%`, {
            sticky: true,
            className: 'district-tooltip'
        });

        // Popup on click with detailed info
        layer.bindPopup(`
      <div class="popup-title">${props.road_name || 'Дорога'}</div>
      <div class="popup-row">
        <span class="popup-label">Загруженность:</span>
        <span class="popup-value ${level}">${congestionPercent}%</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Скорость:</span>
        <span class="popup-value">${props.speed_kmh || '—'} км/ч</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Время:</span>
        <span class="popup-value">${props.timestamp ? new Date(props.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : '—'}</span>
      </div>
    `);
    };

    // Handle district layer
    const onEachDistrictFeature = (feature, layer) => {
        layer.bindTooltip(feature.properties?.name || 'Пилотная зона', {
            permanent: false,
            className: 'district-tooltip'
        });
    };

    // Callback when map is ready
    const handleMapCreated = (map) => {
        mapRef.current = map;
        onMapReady?.(map);
    };

    return (
        <div className="map-container">
            <MapContainer
                center={BISHKEK_CENTER}
                zoom={DEFAULT_ZOOM}
                ref={(map) => map && handleMapCreated(map)}
                style={{ height: '100%', width: '100%' }}
            >
                {/* Map Controller for view changes */}
                <MapController
                    center={BISHKEK_CENTER}
                    searchLocation={searchLocation}
                    userLocation={userLocation}
                />

                {/* OpenStreetMap tiles */}
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Central district boundary */}
                <GeoJSON
                    key="central-district"
                    data={centralDistrict}
                    style={districtStyle}
                    onEachFeature={onEachDistrictFeature}
                />

                {/* Traffic overlay layer */}
                {trafficData && (
                    <GeoJSON
                        key={JSON.stringify(trafficData)}
                        data={trafficData}
                        style={trafficStyle}
                        onEachFeature={onEachTrafficFeature}
                    />
                )}

                {/* Search result marker */}
                {searchLocation && (
                    <Marker
                        position={[searchLocation.lat, searchLocation.lng]}
                        icon={searchMarkerIcon}
                    >
                        <Popup>
                            <div className="popup-title">
                                {searchLocation.name?.split(',')[0] || 'Выбранное место'}
                            </div>
                        </Popup>
                    </Marker>
                )}

                {/* User location marker */}
                {userLocation && (
                    <Marker
                        position={[userLocation.lat, userLocation.lng]}
                        icon={userLocationIcon}
                    >
                        <Popup>
                            <div className="popup-title">Моё местоположение</div>
                        </Popup>
                    </Marker>
                )}
            </MapContainer>

            {/* Geolocation FAB */}
            <button
                className={`fab fab-geolocation ${isLocating ? 'locating' : ''}`}
                onClick={onLocateMe}
                title="Моё местоположение"
            >
                <Crosshair size={22} />
            </button>

            {/* Legend */}
            <Legend />
        </div>
    );
}
