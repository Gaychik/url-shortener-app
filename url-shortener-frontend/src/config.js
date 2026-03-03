// central configuration for constants derived from environment variables
// Vite exposes env vars prefixed with VITE_ through import.meta.env

export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
