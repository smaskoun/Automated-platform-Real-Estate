// src/App.jsx - NEW SIMPLIFIED CODE

import React from 'react';
import Dashboard from './Dashboard.jsx';

// We will create a "mock" user to pass to the dashboard,
// since we are skipping the real login process for now.
const mockUser = { id: 1, username: 'Test User' };

function App() {
  // This simplified App component no longer shows a login form.
  // It immediately renders the main Dashboard.
  // We pass the mock user and an empty logout function.
  return <Dashboard user={mockUser} onLogout={() => {}} />;
}

export default App;
