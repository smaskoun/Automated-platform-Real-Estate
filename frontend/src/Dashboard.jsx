// frontend/src/Dashboard.jsx - NEW INTERACTIVE VERSION

import React, { useState } from 'react';
import styles from './Dashboard.module.css';

// Import all the manager components
import BrandVoiceManager from './BrandVoiceManager.jsx';
import SocialMediaManager from './SocialMediaManager.jsx'; // The new component we just created

// A placeholder component for pages we haven't built yet
const Placeholder = ({ title }) => (
  <div style={{ padding: '20px', color: '#999' }}>
    <h2>{title}</h2>
    <p>This feature is under construction.</p>
  </div>
);

function Dashboard({ user, onLogout }) {
  // State to keep track of the currently active page
  const [activePage, setActivePage] = useState('brand-voices');

  // A helper function to render the correct component based on the active page
  const renderActivePageComponent = () => {
    switch (activePage) {
      case 'brand-voices':
        return <BrandVoiceManager user={user} />;
      case 'social-media':
        return <SocialMediaManager user={user} />;
      case 'seo-tools':
        return <Placeholder title="SEO Tools" />;
      case 'ab-testing':
        return <Placeholder title="A/B Testing" />;
      default:
        return <BrandVoiceManager user={user} />;
    }
  };

  // A helper function to get the title for the header
  const getHeaderTitle = () => {
    switch (activePage) {
      case 'brand-voices':
        return 'Brand & Content Generation';
      case 'social-media':
        return 'Social Media Post Manager';
      case 'seo-tools':
        return 'SEO Content Tools';
      case 'ab-testing':
        return 'A/B Testing Dashboard';
      default:
        return 'Dashboard';
    }
  };

  return (
    <div className={styles.dashboard}>
      <nav className={styles.sidebar}>
        <h2 className={styles.sidebarTitle}>Real Estate AI</h2>
        <ul>
          {/* Each list item now uses onClick to set the active page */}
          <li 
            className={activePage === 'brand-voices' ? styles.active : ''}
            onClick={() => setActivePage('brand-voices')}
          >
            Brand Voices
          </li>
          <li
            className={activePage === 'social-media' ? styles.active : ''}
            onClick={() => setActivePage('social-media')}
          >
            Social Media Posts
          </li>
          <li
            className={activePage === 'seo-tools' ? styles.active : ''}
            onClick={() => setActivePage('seo-tools')}
          >
            SEO Tools
          </li>
          <li
            className={activePage === 'ab-testing' ? styles.active : ''}
            onClick={() => setActivePage('ab-testing')}
          >
            A/B Testing
          </li>
        </ul>
        <div className={styles.userProfile}>
          <span>{user.username}</span>
          <button onClick={onLogout} className={styles.logoutButton}>Logout</button>
        </div>
      </nav>
      <main className={styles.mainContent}>
        <header className={styles.mainHeader}>
          <h1>{getHeaderTitle()}</h1>
        </header>
        <div className={styles.contentArea}>
          {renderActivePageComponent()}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
