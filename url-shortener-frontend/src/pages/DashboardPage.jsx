import React, { useState, useEffect } from 'react';
import axios from 'axios';
// библиотека выдает именованные экспорты, поэтому мы берём нужный компонент
import { QRCodeCanvas } from 'qrcode.react';
import { useAuth } from '../context/useAuth';
import { API_URL } from '../config';

export default function DashboardPage() {
    const { token } = useAuth();
    const [links, setLinks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [qrVisible, setQrVisible] = useState({});

    const toggleQrCode = (linkId) => {
        setQrVisible(prev => ({ ...prev, [linkId]: !prev[linkId] }));
    };

    // Функция для загрузки ссылок
    const fetchLinks = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/users/me/links`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setLinks(response.data);
            console.log("Fetched links:", response.data);
        } catch (err) {
            setError('Не удалось загрузить ссылки. Попробуйте войти снова.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) {
            fetchLinks();
            
            // Интервал для периодического обновления каждые 5 секунд
            const interval = setInterval(() => {
                fetchLinks();
            }, 5000);

            // Слушатель для обновления при возврате на вкладку
            const handleVisibilityChange = () => {
                if (!document.hidden) {
                    fetchLinks();
                }
            };

            document.addEventListener('visibilitychange', handleVisibilityChange);

            // Очистка при размонтировании компонента
            return () => {
                clearInterval(interval);
                document.removeEventListener('visibilitychange', handleVisibilityChange);
            };
        }
    }, [token]);

    if (loading) return <p className="text-center text-slate-400">Загрузка...</p>;
    if (error) return <p className="text-center text-red-400">{error}</p>;

    return (
        <div className="bg-slate-800 p-4 sm:p-6 rounded-xl shadow-2xl">
            <h1 className="text-3xl font-bold mb-6 text-white">Личный кабинет</h1>
            {links.length === 0 ? (
                <p className="text-center text-slate-400 py-4">У вас пока нет ссылок. Создайте первую на главной странице!</p>
            ) : (
                // АДАПТАЦИЯ: обертка для горизонтального скролла на мобильных
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-slate-800">
                        <thead className="border-b border-slate-700">
                            <tr>
                                <th className="py-3 px-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Оригинальный URL</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Короткая ссылка</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Клики</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Действия</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {links.map(link => {
                                const shortUrl = `${API_URL}/${link.short_code}`;
                                return (
                                    <React.Fragment key={link.id}>
                                        <tr className="hover:bg-slate-700/50 transition-colors duration-200">
                                            <td className="py-4 px-4 whitespace-nowrap max-w-xs truncate text-sm text-slate-300" title={link.original_url}>{link.original_url}</td>
                                            <td className="py-4 px-4 whitespace-nowrap text-sm">
                                                <a href={shortUrl} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{shortUrl}</a>
                                            </td>
                                            <td className="py-4 px-4 whitespace-nowrap text-sm font-medium text-white">{link.total_clicks ?? 0}</td>
                                            <td className="py-4 px-4 whitespace-nowrap text-sm">
                                                <button onClick={() => toggleQrCode(link.id)} className="bg-slate-600 text-white px-3 py-1 rounded-md hover:bg-slate-500 text-xs transition-colors duration-200">
                                                    {qrVisible[link.id] ? 'Скрыть' : 'QR-код'}
                                                </button>
                                            </td>
                                        </tr>
                                        {qrVisible[link.id] && (
                                            <tr>
                                                <td colSpan="4" className="p-4 text-center bg-gray-50">
                                                    <div className="inline-block p-4 bg-white rounded-lg shadow">
                                                        {/* используем QRCodeCanvas из пакета */}
                                                <QRCodeCanvas value={shortUrl} size={128} />
                                                        <p className="mt-2 text-sm text-gray-600">QR-код для вашей ссылки</p>
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
