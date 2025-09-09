// frontend/src/App.jsx - FINAL INTEGRATED CODE
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import all page components
import Dashboard from './Dashboard.jsx';
import AccountManager from './AccountManager.jsx';
import BrandVoiceManager from './BrandVoiceManager.jsx';
import SocialMediaManager from './SocialMediaManager.jsx';
import MarketAnalysis from './MarketAnalysis.jsx';

// We will create a "mock" user to pass to the dashboard.
const mockUser = { id: 1, username: 'Test User' };

function App() {
  return (
    <Router>
      <Routes>
        {/* The Dashboard component now acts as a layout for all other pages */}
        <Route path="/" element={<Dashboard user={mockUser} onLogout={() => {}} />}>
          {/* The default page shown at the "/" path */}
          <Route index element={<AccountManager user={mockUser} />} />
          
          {/* Other pages nested inside the dashboard */}
          <Route path="brand-voices" element={<BrandVoiceManager user={mockUser} />} />
          <Route path="social-media" element={<SocialMediaManager user={mockUser} />} />
          <Route path="market-analysis" element={<MarketAnalysis />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
