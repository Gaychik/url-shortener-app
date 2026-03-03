import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

const ProtectedRoute = ({ children }) => {
    const { token } = useAuth();
    
    if (!token) {
        // Если токена нет, перенаправляем на страницу входа
        return <Navigate to="/login" />;
    }

    return children;
};

export default ProtectedRoute;
