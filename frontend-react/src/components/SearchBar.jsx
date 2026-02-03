import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { searchAddress } from '../api';

/**
 * SearchBar component with Nominatim autocomplete
 * Features debounced search (500ms) and keyboard navigation
 */
export default function SearchBar({ onLocationSelect, onError }) {
    const [query, setQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);

    const inputRef = useRef(null);
    const debounceRef = useRef(null);

    // Debounced search function
    const performSearch = useCallback(async (searchQuery) => {
        if (searchQuery.trim().length < 2) {
            setSuggestions([]);
            return;
        }

        setIsLoading(true);
        try {
            const results = await searchAddress(searchQuery);
            setSuggestions(results);

            if (results.length === 0) {
                // Don't show error for empty results during typing
            }
        } catch (error) {
            console.error('Search error:', error);
            onError?.('Ошибка поиска адреса');
        } finally {
            setIsLoading(false);
        }
    }, [onError]);

    // Debounce effect
    useEffect(() => {
        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        if (query.trim()) {
            debounceRef.current = setTimeout(() => {
                performSearch(query);
            }, 500); // 500ms debounce
        } else {
            setSuggestions([]);
        }

        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current);
            }
        };
    }, [query, performSearch]);

    // Handle suggestion selection
    const handleSelect = (suggestion) => {
        const lat = parseFloat(suggestion.lat);
        const lon = parseFloat(suggestion.lon);

        setQuery(suggestion.display_name.split(',')[0]);
        setSuggestions([]);
        setShowSuggestions(false);

        onLocationSelect?.({
            lat,
            lng: lon,
            name: suggestion.display_name
        });
    };

    // Handle keyboard navigation
    const handleKeyDown = (e) => {
        if (!showSuggestions || suggestions.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setSelectedIndex((prev) =>
                    prev < suggestions.length - 1 ? prev + 1 : prev
                );
                break;
            case 'ArrowUp':
                e.preventDefault();
                setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && suggestions[selectedIndex]) {
                    handleSelect(suggestions[selectedIndex]);
                }
                break;
            case 'Escape':
                setShowSuggestions(false);
                setSelectedIndex(-1);
                break;
        }
    };

    // Clear search
    const handleClear = () => {
        setQuery('');
        setSuggestions([]);
        setShowSuggestions(false);
        inputRef.current?.focus();
    };

    // Format address for display
    const formatAddress = (suggestion) => {
        const parts = suggestion.display_name.split(',').slice(1, 3);
        return parts.join(',').trim();
    };

    return (
        <div className="search-container">
            <div className="search-input-wrapper">
                <Search className="search-icon" size={18} />
                <input
                    ref={inputRef}
                    type="text"
                    className="search-input"
                    placeholder="Поиск адреса..."
                    value={query}
                    onChange={(e) => {
                        setQuery(e.target.value);
                        setShowSuggestions(true);
                        setSelectedIndex(-1);
                    }}
                    onFocus={() => setShowSuggestions(true)}
                    onBlur={() => {
                        // Delay to allow click on suggestions
                        setTimeout(() => setShowSuggestions(false), 200);
                    }}
                    onKeyDown={handleKeyDown}
                />
                {query && (
                    <button className="search-clear" onClick={handleClear}>
                        {isLoading ? (
                            <Loader2 size={16} className="loading-spinner" />
                        ) : (
                            <X size={16} />
                        )}
                    </button>
                )}
            </div>

            {showSuggestions && (query.length >= 2 || suggestions.length > 0) && (
                <div className="search-suggestions">
                    {isLoading && suggestions.length === 0 && (
                        <div className="search-loading">Поиск...</div>
                    )}

                    {!isLoading && suggestions.length === 0 && query.length >= 2 && (
                        <div className="search-no-results">Ничего не найдено</div>
                    )}

                    {suggestions.map((suggestion, index) => (
                        <div
                            key={suggestion.place_id}
                            className={`search-suggestion-item ${index === selectedIndex ? 'selected' : ''
                                }`}
                            onClick={() => handleSelect(suggestion)}
                            style={{
                                background: index === selectedIndex ? 'var(--color-bg-hover)' : undefined
                            }}
                        >
                            <div className="search-suggestion-name">
                                {suggestion.display_name.split(',')[0]}
                            </div>
                            <div className="search-suggestion-address">
                                {formatAddress(suggestion)}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
