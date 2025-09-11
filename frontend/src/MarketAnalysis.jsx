import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';

// Use the environment variable for the API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState('');

  const fetchMarketData = async () => {
    setLoading(true);
    setError('');
    try {
      // UPDATED: Call the correct market analysis endpoint
      const response = await axios.get(`${API_BASE_URL}/api/market-analysis/market-analysis`);
      setMarketData(response.data);
    } catch (err) {
      setError('Failed to fetch live market data. Displaying sample data if available.');
      console.error(err);
      // Attempt to set sample data from error response if backend provides it
      if (err.response && err.response.data) {
        setMarketData(err.response.data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketData();
  }, []);

  // NEW: Function to handle PDF download
  const handleDownloadReport = async () => {
    setIsDownloading(true);
    setDownloadError('');
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market-analysis/download-report`, {
        responseType: 'blob', // Important for handling file downloads
      });

      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from content-disposition header, or set a default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'market-report.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch.length === 2) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      setDownloadError('Failed to generate PDF report. Please try again.');
      console.error('Download error:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  const renderReport = () => {
    if (loading) return <p className="text-center p-8">Fetching live market data...</p>;
    if (error && !marketData) return <p className="text-center p-8 text-red-500">{error}</p>;
    if (!marketData) return <p className="text-center p-8">No data available.</p>;

    // Adjusted data structure to match new backend
    const stats = marketData.stats?.latest || {};
    const salesByType = marketData.stats?.property_type_distribution ? 
      Object.entries(marketData.stats.property_type_distribution).map(([name, sales]) => ({ name, sales })) : [];
    const yoyChange = marketData.stats?.year_over_year_change || {};

    const formatCurrency = (num) => `$${new Intl.NumberFormat('en-US').format(num || 0)}`;
    const formatNumber = (num) => new Intl.NumberFormat('en-US').format(num || 0);
    const formatPriceK = (num) => `$${((num || 0) / 1000).toFixed(0)}K`;

    return (
      <div className="space-y-8">
        {/* Display a notification if showing sample data */}
        {marketData.source === 'Sample Data' && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4" role="alert">
            <p className="font-bold">Notice</p>
            <p>{marketData.note || 'Could not fetch live data. Displaying sample information.'}</p>
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard 
            title="Average Price" 
            value={formatCurrency(stats.average_price)}
            change={yoyChange.average_price_pct}
            changeColor={(yoyChange.average_price_pct || 0) > 0 ? 'text-green-600' : 'text-red-600'}
          />
          <StatCard 
            title="Total Sales" 
            value={formatNumber(stats.total_sales)}
            change={yoyChange.total_sales_pct}
            changeColor={(yoyChange.total_sales_pct || 0) > 0 ? 'text-green-600' : 'text-red-600'}
          />
          <StatCard 
            title="New Listings" 
            value={formatNumber(stats.new_listings)}
            change={yoyChange.new_listings_pct}
            changeColor={(yoyChange.new_listings_pct || 0) > 0 ? 'text-green-600' : 'text-red-600'}
          />
          <StatCard 
            title="Months of Supply" 
            value={stats.months_of_supply || 'N/A'}
          />
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-bold mb-4">Sales by Property Type</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={salesByType} margin={{ top: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value) => formatNumber(value)} />
              <Bar dataKey="sales" fill="#3b82f6" name="Number of Sales">
                <LabelList dataKey="sales" position="top" style={{ fill: '#333' }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-1">Windsor-Essex Market Analysis</h1>
          <p className="text-md text-gray-500">
            {loading ? 'Fetching...' : (marketData?.period || 'Report Details')}
          </p>
        </div>
        {/* NEW: Download Button with loading and error states */}
        <div>
          <button
            onClick={handleDownloadReport}
            disabled={isDownloading || loading}
            className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300"
          >
            {isDownloading ? 'Generating PDF...' : 'Download Report'}
          </button>
          {downloadError && <p className="text-red-500 text-sm mt-2">{downloadError}</p>}
        </div>
      </div>
      {renderReport()}
    </div>
  );
}

export default MarketAnalysis;
