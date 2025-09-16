import React from 'react';
// We need to import Navigate for the default redirect
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import the new layout and all page components
import DashboardLayout from './Dashboard.jsx';
import AccountManager from './AccountManager.jsx';
import BrandVoiceManager from './BrandVoiceManager.jsx';
import SocialMediaManager from './SocialMediaManager.jsx';
import SeoTools from './SeoTools.jsx';

// We will create a "mock" user to pass to the layout.
const mockUser = { id: 1, username: 'Test User' };

function App() {
  return (
    <Router>
      <Routes>
        {/* The DashboardLayout component now acts as the main layout for all pages */}
        <Route path="/" element={<DashboardLayout user={mockUser} onLogout={() => {}} />}>
          
          {/* Redirect from the base path "/" to the default "/accounts" page */}
          <Route index element={<Navigate to="/accounts" replace />} />
          
          {/* All pages are now nested inside the layout and have their own paths */}
          <Route path="accounts" element={<AccountManager user={mockUser} />} />
          <Route path="brand-voices" element={<BrandVoiceManager user={mockUser} />} />
          <Route path="social-media" element={<SocialMediaManager user={mockUser} />} />
          <Route path="seo-tools" element={<SeoTools user={mockUser} />} />

        </Route>
      </Routes>
    </Router>
  );
}

export default App;
