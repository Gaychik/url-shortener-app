import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../config';

export default function ShortenerForm() {
    const [originalUrl, setOriginalUrl] = useState('');
    const [shortenedLink, setShortenedLink] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [expirationDate, setExpirationDate] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setShortenedLink(null);
        setLoading(true);

        try {
            const payload = { original_url: originalUrl };
            if (expirationDate) {
                payload.expiration_date = new Date(expirationDate).toISOString();
            }
            const response = await axios.post(`${API_URL}/api/links`, payload);
            setShortenedLink(`${API_URL}/${response.data.short_code}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Произошла ошибка');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        if (shortenedLink) {
            navigator.clipboard.writeText(shortenedLink);
            alert('Ссылка скопирована!');
        }
    };

    return (
        <div className="max-w-3xl mx-auto bg-slate-800 p-6 sm:p-8 rounded-xl shadow-2xl">
            <h1 className="text-3xl sm:text-4xl font-bold text-center text-white mb-6">Сократите вашу ссылку</h1>
            <form onSubmit={handleSubmit} className="space-y-5">
                <input
                    type="url"
                    className="w-full p-4 bg-slate-700 text-white border-2 border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-all duration-300"
                    placeholder="https://example.com/very/long/url/to/shorten"
                    value={originalUrl}
                    onChange={(e) => setOriginalUrl(e.target.value)}
                    required
                />
                <div>
                    <label htmlFor="expiration" className="block text-sm font-medium text-slate-400 mb-2">
                        Действительна до (необязательно):
                    </label>
                    {/* УЛУЧШЕНО: стилизованный календарь для темной темы */}
                    <input
                        type="datetime-local"
                        id="expiration"
                        value={expirationDate}
                        onChange={(e) => setExpirationDate(e.target.value)}
                        className="w-full p-4 bg-slate-700 text-white border-2 border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-all duration-300 [color-scheme:dark]"
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-600 text-white py-4 rounded-lg font-bold text-lg hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-all duration-300 ease-in-out transform hover:scale-105"
                    disabled={loading}
                >
                    {loading ? 'Сокращаем...' : 'Сократить'}
                </button>
            </form>

            {error && <p className="text-red-400 text-center mt-4 animate-pulse">{error}</p>}

            {shortenedLink && (
                <div className="mt-8 p-4 bg-slate-900/50 border border-slate-700 rounded-xl">
                    <p className="text-center mb-3 text-slate-300">Ваша короткая ссылка:</p>
                    <div className="flex flex-col sm:flex-row items-center justify-between bg-slate-800 p-3 rounded-lg shadow-md">
                        <a href={shortenedLink} target="_blank" rel="noopener noreferrer" className="text-blue-400 font-medium break-all hover:underline mb-3 sm:mb-0">
                            {shortenedLink}
                        </a>
                        <button onClick={copyToClipboard} className="ml-0 sm:ml-4 w-full sm:w-auto flex-shrink-0 bg-slate-600 text-white px-5 py-2 rounded-md hover:bg-slate-500 transition-colors duration-200">
                            Копировать
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
