import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { format } from 'date-fns';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const StatCard = ({ title, value }) => (
  <div className="bg-white p-4 rounded-lg shadow-md text-center">
    <h4 className="text-md font-medium text-gray-500">{title}</h4>
    <p className="text-3xl font-bold mt-1">{value}</p>
  </div>
);

function MarketAnalysis() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false); // Don't load on initial render
  const [error, setError] = useState('');
  
  // State for the date picker
  const [startDate, setStartDate] = useState(new Date(new Date().setMonth(new Date().getMonth() - 3))); // Default to 3 months ago
  const [endDate, setEndDate] = useState(new Date());

  // Fetch historical data based on date range
  const fetchHistoricalData = async () => {
    if (!startDate || !endDate) {
      setError('Please select a start and end date.');
      return;
    }
    
    setLoading(true);
    setError('');
    setMarketData(null); // Clear previous data

    const formattedStartDate = format(startDate, 'yyyy-MM');
    const formattedEndDate = format(endDate, 'yyyy-MM');

    try {
      const response = await axios.get(`${API_BASE_URL}/api/market-analysis/historical`, {
        params: {
          start_date: formattedStartDate,
          end_date: formattedEndDate,
        },
      });
      setMarketData(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to fetch market data for the selected period.';
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Render the main analysis content
  const renderReport = () => {
    if (loading) return <p className="text-center p-8">Fetching analysis for the selected period...</p>;
    if (error) return <p className="text-center p-8 text-red-500">{error}</p>;
    if (!marketData) return <p className="text-center p-8 text-gray-500">Select a date range and click "Get Analysis" to begin.</p>;

    const { key_metrics, sales_by_type, monthly_breakdown } = marketData;

    const formatCurrency = (num) => `$${new Intl.NumberFormat('en-US').format(num || 0)}`;
    const formatNumber = (num) => new Intl.NumberFormat('en-US').format(num || 0);

    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard 
            title="Average Price" 
            value={formatCurrency(key_metrics.average_price)}
          />
          <StatCard 
            title="Total Sales" 
            value={formatNumber(key_metrics.total_sales)}
          />
          <StatCard 
            title="New Listings" 
            value={formatNumber(key_metrics.new_listings)}
          />
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-bold mb-4">Total Sales by Property Type</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sales_by_type} margin={{ top: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value) => formatNumber(value)} />
              <Bar dataKey="sales" fill="#3b82f6" name="Total Sales">
                <LabelList dataKey="sales" position="top" style={{ fill: '#333' }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* New chart for monthly trends */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-bold mb-4">Monthly Sales Trend</h4>
           <ResponsiveContainer width="100%" height={300}>
             <BarChart data={monthly_breakdown} margin={{ top: 20 }}>
               <CartesianGrid strokeDasharray="3 3" vertical={false} />
               <XAxis dataKey="period" tick={{ fontSize: 12 }} />
               <YAxis yAxisId="left" orientation="left" stroke="#8884d8" label={{ value: 'Total Sales', angle: -90, position: 'insideLeft' }} />
               <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" label={{ value: 'Average Price', angle: 90, position: 'insideRight' }} tickFormatter={(val) => `$${(val/1000)}k`} />
               <Tooltip formatter={(value, name) => name === 'Average Price' ? formatCurrency(value) : formatNumber(value)} />
               <Legend />
               <Bar yAxisId="left" dataKey="key_metrics.total_sales" fill="#8884d8" name="Total Sales" />
               <Bar yAxisId="right" dataKey="key_metrics.average_price" fill="#82ca9d" name="Average Price" />
             </BarChart>
           </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Windsor-Essex Market Analysis</h1>
      
      {/* New Control Bar for Date Selection */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-8 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <label htmlFor="start-date" className="font-medium text-gray-700">From:</label>
          <DatePicker
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            dateFormat="MMM yyyy"
            showMonthYearPicker
            className="w-32 p-2 border border-gray-300 rounded-md"
          />
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="end-date" className="font-medium text-gray-700">To:</label>
          <DatePicker
            selected={endDate}
            onChange={(date) => setEndDate(date)}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            dateFormat="MMM yyyy"
            showMonthYearPicker
            className="w-32 p-2 border border-gray-300 rounded-md"
          />
        </div>
        <button
          onClick={fetchHistoricalData}
          disabled={loading}
          className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
        >
          {loading ? 'Loading...' : 'Get Analysis'}
        </button>
        <button
          disabled={true} // Disabled for now
          className="bg-gray-400 text-white font-bold py-2 px-4 rounded-lg shadow-md cursor-not-allowed"
        >
          Download Report
        </button>
      </div>

      {renderReport()}
    </div>
  );
}

export default MarketAnalysis;
