import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../config';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Настраиваем axios, чтобы он всегда отправлял токен, если он есть
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
        }
    }, [token]);

    const login = async (email, password) => {
        setLoading(true);
        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);
            //console.log("Attempting login with:", email + " / " + password);
           
            const response = await axios.post(`${API_URL}/api/auth/login`, formData);
            setToken(response.data.access_token);
            //console.log("Login successful:", response.data.access_token);

            navigate('/dashboard');
        } catch (error) {
            console.error("Login failed:", error);
            alert('Неверный email или пароль');
        } finally {
            setLoading(false);
        }
    };

    const register = async (email, password) => {
        setLoading(true);
        try {
            await axios.post(`${API_URL}/api/auth/register`, { email, password });
            alert('Регистрация прошла успешно! Теперь вы можете войти.');
            navigate('/login');
        } catch (error) {
            console.error("Registration failed:", error);
            alert(error.response?.data?.detail || 'Ошибка регистрации');
        } finally {
            setLoading(false);
        }
    };
    
    const logout = () => {
        setToken(null);
        navigate('/login');
    };

    const value = {
        token,
        login,
        register,
        logout,
        loading
    };
    
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

// // Хук для удобного использования контекста
// export const   useAuth = () => {
//     return useContext(AuthContext);
// };
