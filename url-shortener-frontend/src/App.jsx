import React from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom'; // Импортируем useNavigate
import { useAuth } from './context/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';

function App() {
    const { token, logout } = useAuth();
    const navigate = useNavigate(); // Хук для навигации

    // Стили для кнопок-ссылок, чтобы избежать дублирования
    const navLinkStyle = "text-slate-300 hover:text-white transition-colors duration-200";
    const navButtonStyle = "bg-blue-600 text-white px-4 py-2 rounded-md font-semibold hover:bg-blue-700 transition-all duration-300 ease-in-out transform hover:scale-105";

    return (
        <div className="min-h-screen bg-slate-900 text-slate-200 font-sans">
            <nav className="bg-slate-800/70 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <Link to="/" className="text-2xl font-bold text-white">Short.ly</Link>
                        <div className="flex items-center space-x-4">
                            {token ? (
                                <>
                                    <Link to="/dashboard" className={navLinkStyle}>Личный кабинет</Link>
                                    <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded-md font-semibold hover:bg-red-600 transition-all duration-300 ease-in-out transform hover:scale-105">
                                        Выйти
                                    </button>
                                </>
                            ) : (
                                <>
                                    {/* ИСПРАВЛЕНО: Теперь это настоящая кнопка, а не ссылка */}
                                    <button onClick={() => navigate('/login')} className={navLinkStyle}>Войти</button>
                                    <button onClick={() => navigate('/register')} className={navButtonStyle}>Регистрация</button>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            <main className="py-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route
                            path="/dashboard"
                            element={<ProtectedRoute><DashboardPage /></ProtectedRoute>}
                        />
                    </Routes>
                </div>
            </main>
        </div>
    );
}

export default App;

