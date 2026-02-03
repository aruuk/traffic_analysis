import React, { useEffect, useState } from 'react';
import { Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

/**
 * Toast notification component
 * Displays temporary messages that auto-dismiss
 */

const ICONS = {
    info: Info,
    success: CheckCircle,
    warning: AlertTriangle,
    error: XCircle
};

export default function Toast({ message, type = 'info', onClose }) {
    const [exiting, setExiting] = useState(false);
    const Icon = ICONS[type] || ICONS.info;

    useEffect(() => {
        // Auto-dismiss after 4 seconds
        const timer = setTimeout(() => {
            setExiting(true);
            setTimeout(onClose, 300); // Wait for animation
        }, 4000);

        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`toast ${type} ${exiting ? 'exiting' : ''}`}>
            <Icon className="toast-icon" size={18} />
            <span>{message}</span>
        </div>
    );
}

/**
 * Toast container component
 * Manages multiple toast notifications
 */
export function ToastContainer({ toasts, removeToast }) {
    if (toasts.length === 0) return null;

    return (
        <div className="toast-container">
            {toasts.map((toast) => (
                <Toast
                    key={toast.id}
                    message={toast.message}
                    type={toast.type}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </div>
    );
}
