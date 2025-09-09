// src/App.jsx - UPDATED CODE
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './Dashboard.jsx';
import MarketAnalysis from './components/MarketAnalysis.jsx'; // Assuming you created this file in components/

// We will create a "mock" user to pass to the dashboard,
// since we are skipping the real login process for now.
const mockUser = { id: 1, username: 'Test User' };

function App( ) {
  return (
    <Router>
      <div>
        {/* Simple Navigation */}
        <nav className="bg-gray-800 text-white p-4">
          <ul className="flex space-x-4">
            <li>
              <Link to="/">Dashboard</Link>
            </li>
            <li>
              <Link to="/market-analysis">Market Analysis</Link>
            </li>
          </ul>
        </nav>

        {/* Route Definitions */}
        <Routes>
          <Route 
            path="/" 
            element={<Dashboard user={mockUser} onLogout={() => {}} />} 
          />
          <Route 
            path="/market-analysis" 
            element={<MarketAnalysis />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
