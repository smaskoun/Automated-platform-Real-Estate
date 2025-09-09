// frontend/src/Dashboard.jsx - FULL REPLACEMENT

import React from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import styles from './Dashboard.module.css';

function Dashboard({ user, onLogout }) {
  const location = useLocation(); // Hook to get the current URL path

  return (
    <div className={styles.dashboard}>
      <nav className={styles.sidebar}>
        <h1 className={styles.logo}>Real Estate AI</h1>
        <ul>
          {/* Each item is now a <Link> component */}
          <li className={location.pathname === '/' ? styles.active : ''}>
            <Link to="/">Accounts</Link>
          </li>
          <li className={location.pathname === '/brand-voices' ? styles.active : ''}>
            <Link to="/brand-voices">Brand Voices</Link>
          </li>
          <li className={location.pathname === '/social-media' ? styles.active : ''}>
            <Link to="/social-media">Social Media Posts</Link>
          </li>
          {/* NEW LINK FOR MARKET ANALYSIS */}
          <li className={location.pathname === '/market-analysis' ? styles.active : ''}>
            <Link to="/market-analysis">Market Analysis</Link>
          </li>
          <li className={styles.disabled} title="Coming Soon">
            SEO Tools
          </li>
          <li className={styles.disabled} title="Coming Soon">
            A/B Testing
          </li>
        </ul>
        <div className={styles.userSection}>
          <span>{user.username}</span>
          <button onClick={onLogout} className={styles.logoutButton}>Logout</button>
        </div>
      </nav>
      <main className={styles.mainContent}>
        {/* Outlet renders the component for the current route */}
        <Outlet />
      </main>
    </div>
  );
}

export default Dashboard;
