import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './src/App.jsx'
import './src/styles.css'

console.log('Main script running');
ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
)
