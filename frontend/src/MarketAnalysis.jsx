import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const MarketAnalysis = () => {
    const [source, setSource] = useState('cmhc');
    const [marketData, setMarketData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGenerateReport = async () => {
        setLoading(true);
        setError('');
        setMarketData(null);

        // <<< START OF CHANGES
        const API_URL = import.meta.env.VITE_API_BASE_URL;
        let path = '';
        // <<< END OF CHANGES

        if (source === 'cmhc') {
            path = '/api/market-analysis/cmhc-rental-market';
        } else if (source === 'statcan') {
            path = '/api/market-analysis/statcan-housing-starts';
        } else if (source === 'wecar') {
            path = '/api/market-analysis/wecar-sales';
        }

        try {
            // <<< MODIFIED LINE
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
        if (!marketData) return null;

        const rentData = [
            { name: 'Bachelor', Windsor: marketData.windsor.avg_rent_bachelor, Ontario: marketData.ontario.avg_rent_bachelor },
            { name: '1-Bedroom', Windsor: marketData.windsor.avg_rent_1_bedroom, Ontario: marketData.ontario.avg_rent_1_bedroom },
            { name: '2-Bedroom', Windsor: marketData.windsor.avg_rent_2_bedroom, Ontario: marketData.ontario.avg_rent_2_bedroom },
            { name: '3-Bedroom+', Windsor: marketData.windsor.avg_rent_3_bedroom_plus, Ontario: marketData.ontario.avg_rent_3_bedroom_plus },
        ];

        return (
            <div>
                <h3 className="text-2xl font-semibold mb-4">CMHC Rental Market Report</h3>
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
                <h4 className="text-xl font-semibold mb-2">Average Rent Comparison</h4>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={rentData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="Windsor" fill="#8884d8" />
                        <Bar dataKey="Ontario" fill="#82ca9d" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        );
    };
    
    const renderStatCanReport = () => {
        if (!marketData || marketData.length === 0) return null;
        return (
            <div>
                <h3 className="text-2xl font-semibold mb-4">Statistics Canada - Housing Starts</h3>
                 <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={marketData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="windsor_starts" name="Windsor Starts" stroke="#8884d8" />
                        <Line type="monotone" dataKey="ontario_starts" name="Ontario Starts" stroke="#82ca9d" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        );
    };

    const renderWECARReport = () => {
        if (!marketData) return null;
        return (
            <div>
                <h3 className="text-2xl font-semibold mb-4">WECAR Monthly Market Report</h3>
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
                    <option value="cmhc">CMHC Rental Market</option>
                    <option value="statcan">Statistics Canada - Housing Starts</option>
                    <option value="wecar">WECAR - Market Activity</option>
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
                {marketData && source === 'statcan' && renderStatCanReport()}
                {marketData && source === 'wecar' && renderWECARReport()}
            </div>
        </div>
    );
};

export default MarketAnalysis;
