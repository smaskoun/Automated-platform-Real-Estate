import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const StatCard = ({ title, value, change, changeColor }) => (
  <div className="bg-white p-4 rounded-lg shadow-md text-center">
    <h4 className="text-md font-medium text-gray-500">{title}</h4>
    <p className="text-3xl font-bold mt-1">{value}</p>
    {change !== undefined && (
      <p className={`text-sm font-semibold mt-1 ${changeColor}`}>
        {change > 0 ? '▲' : '▼'} {Math.abs(change)}% YoY
      </p>
    )}
  </div>
);

function MarketAnalysis() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchMarketData = async () => {
    setLoading(true);
    setError('');
    try {
      // Call the new automated WECAR endpoint
      const response = await axios.get(`${API_BASE_URL}/api/market-analysis/wecar-market-report`);
      setMarketData(response.data);
    } catch (err) {
      setError('Failed to fetch live market data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchMarketData();
  }, []);

  const renderReport = () => {
    if (loading) return <p className="text-center p-8">Fetching live market data...</p>;
    if (error) return <p className="text-center p-8 text-red-500">{error}</p>;
    if (!marketData) return <p className="text-center p-8">No data available.</p>;

    const { key_metrics, sales_by_type, year_over_year_change } = marketData;

    const formatCurrency = (num) => `$${new Intl.NumberFormat('en-US').format(num)}`;
    const formatNumber = (num) => new Intl.NumberFormat('en-US').format(num);
    const formatPriceK = (num) => `$${(num / 1000).toFixed(0)}K`;

    return (
      <div className="space-y-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard 
            title="Average Price" 
            value={formatCurrency(key_metrics.average_price)}
            change={year_over_year_change.average_price_pct}
            changeColor={year_over_year_change.average_price_pct > 0 ? 'text-green-600' : 'text-red-600'}
          />
          <StatCard 
            title="Total Sales" 
            value={formatNumber(key_metrics.total_sales)}
            change={year_over_year_change.total_sales_pct}
            changeColor={year_over_year_change.total_sales_pct > 0 ? 'text-green-600' : 'text-red-600'}
          />
          <StatCard 
            title="New Listings" 
            value={formatNumber(key_metrics.new_listings)}
            change={year_over_year_change.new_listings_pct}
            changeColor={year_over_year_change.new_listings_pct > 0 ? 'text-green-600' : 'text-red-600'}
          />
          <StatCard 
            title="Months of Supply" 
            value={key_metrics.months_of_supply}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h4 className="text-lg font-bold mb-4">Sales by Property Type</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sales_by_type} margin={{ top: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value) => formatNumber(value)} />
                <Bar dataKey="sales" fill="#8884d8" name="Number of Sales">
                  <LabelList dataKey="sales" position="top" style={{ fill: '#333' }} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h4 className="text-lg font-bold mb-4">Average Price by Property Type</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sales_by_type} margin={{ top: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={formatPriceK} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="average_price" fill="#82ca9d" name="Average Price">
                  <LabelList dataKey="average_price" position="top" formatter={formatPriceK} style={{ fill: '#333' }} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Windsor-Essex Market Analysis</h1>
      <p className="text-md text-gray-500 mb-6">
        {loading ? 'Fetching latest WECAR report...' : (marketData ? marketData.report_period : 'Report Details')}
      </p>
      {renderReport()}
    </div>
  );
}

export default MarketAnalysis;
