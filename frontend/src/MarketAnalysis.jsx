import React, { useState } from 'react';
import axios from 'axios';
// Import the LabelList component to add labels to our bars
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';

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

    // A small helper component for the key metric cards for better styling
    const MetricCard = ({ title, value, bgColor }) => (
        <div className={`${bgColor} p-4 rounded-lg text-center`}>
            <h4 className="text-lg font-bold text-gray-700">{title}</h4>
            <p className="text-3xl text-black">{value}</p>
        </div>
    );

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

                {/* --- IMPROVED: Key Metrics Grid --- */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <MetricCard title="Average Price" value={summary.average_price} bgColor="bg-blue-100" />
                    <MetricCard title="Total Sales" value={summary.total_sales} bgColor="bg-green-100" />
                    <MetricCard title="New Listings" value={summary.new_listings} bgColor="bg-yellow-100" />
                    <MetricCard title="Months of Supply" value={summary.months_of_supply} bgColor="bg-indigo-100" />
                </div>

                {/* Container for the charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    <div>
                        <h4 className="text-xl font-semibold mb-2">Sales by Property Type</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={breakdown} margin={{ top: 20, right: 20, left: -10, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="property_type" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="sales" name="Number of Sales" fill="#8884d8">
                                    {/* --- NEW: Adds labels on top of the bars --- */}
                                    <LabelList dataKey="sales" position="top" />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <div>
                        <h4 className="text-xl font-semibold mb-2">Average Price by Property Type</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={priceBreakdown} margin={{ top: 20, right: 20, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="property_type" />
                                <YAxis 
                                    tickFormatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact' }).format(value)}
                                />
                                <Tooltip 
                                    formatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)}
                                />
                                <Legend />
                                <Bar dataKey="average_price_numeric" name="Average Price" fill="#82ca9d">
                                    {/* --- NEW: Adds labels on top of the bars --- */}
                                    <LabelList 
                                        dataKey="average_price_numeric" 
                                        position="top" 
                                        formatter={(value) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value)}
                                    />
                                </Bar>
                            </BarChart>
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
                <button
                    onClick={handleGenerateReport}
                    disabled={loading}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                >
                    {loading ? 'Generating...' : 'Generate Market Report'}
                </button>
            </div>

            {error && <p className="text-red-500">{error}</p>}

            <div className="mt-6">
                {renderReport()}
            </div>
        </div>
    );
};

export default MarketAnalysis;
