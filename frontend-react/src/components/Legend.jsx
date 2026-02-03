import React from 'react';

/**
 * Legend component for traffic intensity visualization
 * Shows color coding: low (green), medium (orange), high (red)
 */
export default function Legend() {
    return (
        <div className="legend">
            <div className="legend-title">Загруженность</div>
            <div className="legend-items">
                <div className="legend-item">
                    <span className="legend-color low"></span>
                    <span className="legend-label">Низкая</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color medium"></span>
                    <span className="legend-label">Средняя</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color high"></span>
                    <span className="legend-label">Высокая</span>
                </div>
            </div>
        </div>
    );
}
