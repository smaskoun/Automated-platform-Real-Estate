import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MarketAnalysis = () => {
    const [source, setSource] = useState('wecar'); // Default to WECAR now
    const [marketData, setMarketData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGenerateReport = async () => {
        setLoading(true);
        setError('');
        setMarketData(null);

        const API_URL = import.meta.env.VITE_API_BASE_URL;
        let path = '';

        if (source === 'cmhc') {
            path = '/api/market-analysis/cmhc-rental-market';
        } else if (source === 'wecar') {
            path = '/api/market-analysis/wecar-stats';
        }

        try {
            const response = await axios.get(`${API_URL}${path}`);
            setMarketData(response.data);
        } catch (err) {
            setError('Failed to fetch data. Please try again later.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const renderCMHCReport = () => {
        if (!marketData || !marketData.windsor) return null;
        return (
            <div>
                <h3 className="text-2xl font-semibold mb-4">CMHC Rental Market Report (Sample)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                    <div className="bg-gray-100 p-4 rounded-lg text-center">
                        <h4 className="text-lg font-bold">Windsor Vacancy Rate</h4>
                        <p className="text-3xl">{marketData.windsor.vacancy_rate_pct}%</p>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg text-center">
                        <h4 className="text-lg font-bold">Ontario Vacancy Rate</h4>
                        <p className="text-3xl">{marketData.ontario.vacancy_rate_pct}%</p>
                    </div>
                </div>
            </div>
        );
    };
    
    const renderWECARReport = () => {
        if (!marketData || !marketData.average_price) return null;
        return (
            <div>
                <h3 className="text-2xl font-semibold mb-4">WECAR Live Market Report</h3>
                <p className="text-md mb-4 text-gray-600">Report for: {marketData.report_period || 'Latest Month'}</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-100 p-4 rounded-lg text-center">
                        <h4 className="text-lg font-bold">Average Price</h4>
                        <p className="text-3xl">{marketData.average_price || 'N/A'}</p>
                    </div>
                    <div className="bg-green-100 p-4 rounded-lg text-center">
                        <h4 className="text-lg font-bold">Total Sales</h4>
                        <p className="text-3xl">{marketData.total_sales || 'N/A'}</p>
                    </div>
                    <div className="bg-yellow-100 p-4 rounded-lg text-center">
                        <h4 className="text-lg font-bold">New Listings</h4>
                        <p className="text-3xl">{marketData.new_listings || 'N/A'}</p>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-4">Windsor-Essex Market Analysis</h1>
            <div className="flex items-center space-x-4 mb-6">
                <select
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    className="p-2 border rounded"
                >
                    <option value="wecar">WECAR Live Stats</option>
                    <option value="cmhc">CMHC Rental Stats (Sample)</option>
                </select>
                <button
                    onClick={handleGenerateReport}
                    disabled={loading}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                >
                    {loading ? 'Generating...' : 'Generate Report'}
                </button>
            </div>

            {error && <p className="text-red-500">{error}</p>}

            <div className="mt-6">
                {marketData && source === 'cmhc' && renderCMHCReport()}
                {marketData && source === 'wecar' && renderWECARReport()}
            </div>
        </div>
    );
};

export default MarketAnalysis;
