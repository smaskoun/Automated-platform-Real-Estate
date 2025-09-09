import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MarketAnalysis = () => {
    const [marketData, setMarketData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGenerateReport = async () => {
        setLoading(true);
        setError('');
        setMarketData(null);

        const API_URL = import.meta.env.VITE_API_BASE_URL;
        const path = '/api/market-analysis/full-market-report';

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

    const renderReport = () => {
        if (!marketData) return null;

        const { summary, breakdown, report_period } = marketData;
        
        const priceBreakdown = breakdown.map(item => ({
            ...item,
            average_price_numeric: Number(item.average_price.replace(/[^0-9.-]+/g,""))
        }));

        return (
            <div>
                <h3 className="text-2xl font-semibold mb-2">Windsor-Essex Market Report</h3>
                <p className="text-md mb-6 text-gray-500">{report_period}</p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-blue-100 p-4 rounded-lg text-center"><h4 className="text-lg font-bold">Average Price</h4><p className="text-3xl">{summary.average_price}</p></div>
                    <div className="bg-green-100 p-4 rounded-lg text-center"><h4 className="text-lg font-bold">Total Sales</h4><p className="text-3xl">{summary.total_sales}</p></div>
                    <div className="bg-yellow-100 p-4 rounded-lg text-center"><h4 className="text-lg font-bold">New Listings</h4><p className="text-3xl">{summary.new_listings}</p></div>
                    <div className="bg-indigo-100 p-4 rounded-lg text-center"><h4 className="text-lg font-bold">Months of Supply</h4><p className="text-3xl">{summary.months_of_supply}</p></div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div>
                        <h4 className="text-xl font-semibold mb-2">Sales by Property Type</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={breakdown}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="property_type" /><YAxis /><Tooltip /><Legend /><Bar dataKey="sales" name="Number of Sales" fill="#8884d8" /></BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div>
                        <h4 className="text-xl font-semibold mb-2">Average Price by Property Type</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={priceBreakdown}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="property_type" /><YAxis tickFormatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact' }).format(value)} /><Tooltip formatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)} /><Legend /><Bar dataKey="average_price_numeric" name="Average Price" fill="#82ca9d" /></BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-4">Windsor-Essex Market Analysis</h1>
            <div className="flex items-center space-x-4 mb-6">
                <button onClick={handleGenerateReport} disabled={loading} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400">
                    {loading ? 'Generating...' : 'Generate Market Report'}
                </button>
            </div>
            {error && <p className="text-red-500">{error}</p>}
            <div className="mt-6">{renderReport()}</div>
        </div>
    );
};

export default MarketAnalysis;
