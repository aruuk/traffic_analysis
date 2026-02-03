import React from 'react';
import { MapPin } from 'lucide-react';
import SearchBar from './SearchBar';

/**
 * Control Panel component
 * Contains search, time selector, and predict button
 * Responsive: left sidebar on desktop, top panel on mobile
 */
export default function ControlPanel({
    selectedMinutes,
    onMinutesChange,
    onPredict,
    onLocationSelect,
    onError,
    isLoading,
    isMockData
}) {
    const timeOptions = [15, 30, 60];

    return (
        <div className="control-panel">
            <div className="panel-header">
                <h1>🚗 Traffic Predictor</h1>
                <p>Прогноз пробок в Бишкеке</p>
            </div>

            <div className="panel-content">
                {/* Search Section */}
                <div className="panel-section">
                    <div className="panel-section-title">Найти адрес</div>
                    <SearchBar
                        onLocationSelect={onLocationSelect}
                        onError={onError}
                    />
                </div>

                {/* Time Selector Section */}
                <div className="panel-section">
                    <div className="panel-section-title">Прогноз на</div>
                    <div className="segmented-control">
                        {timeOptions.map((minutes) => (
                            <button
                                key={minutes}
                                className={`segmented-option ${selectedMinutes === minutes ? 'active' : ''
                                    }`}
                                onClick={() => onMinutesChange(minutes)}
                            >
                                {minutes} мин
                            </button>
                        ))}
                    </div>
                </div>

                {/* Predict Button */}
                <div className="panel-section">
                    <button
                        className="btn btn-primary"
                        onClick={onPredict}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <>
                                <span className="loading-spinner"></span>
                                Загрузка...
                            </>
                        ) : (
                            <>
                                <MapPin size={18} />
                                Показать прогноз
                            </>
                        )}
                    </button>
                </div>

                {/* Status indicator */}
                {isMockData && (
                    <div className="panel-section">
                        <div className="status-badge mock">
                            <span className="status-dot"></span>
                            Демо-данные (API недоступен)
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
