import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/useAuth';
import { useNavigate } from 'react-router-dom';

export default function RegisterPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { register, loading, token } = useAuth();
    const navigate = useNavigate();

    // Редирект на dashboard если уже залогирован
    useEffect(() => {
        if (token) {
            navigate('/dashboard');
        }
    }, [token, navigate]);

    const handleSubmit = (e) => {
        e.preventDefault();
        register(email, password);
    };

    return (
        <div className="max-w-md mx-auto bg-slate-800 p-8 rounded-xl shadow-2xl">
            <h1 className="text-2xl font-bold text-center mb-6 text-white">Регистрация</h1>
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="email" className="block text-sm font-medium text-slate-400">Email</label>
                    <input
                        id="email"
                        type="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="mt-1 block w-full p-3 bg-slate-700 text-white border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    />
                </div>
                <div>
                    <label htmlFor="password" className="block text-sm font-medium text-slate-400">Пароль</label>
                    <input
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="mt-1 block w-full p-3 bg-slate-700 text-white border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    />
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-3 rounded-md font-semibold hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-all duration-300 ease-in-out transform hover:scale-105"
                >
                    {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                </button>
            </form>
        </div>
    );
}
