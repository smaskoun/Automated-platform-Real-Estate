// frontend/src/Dashboard.jsx - FULL REPLACEMENT

import React, { useState } from 'react';
import styles from './Dashboard.module.css';
import BrandVoiceManager from './BrandVoiceManager.jsx';
import SocialMediaManager from './SocialMediaManager.jsx';
import AccountManager from './AccountManager.jsx'; // Import the new component

function Dashboard({ user, onLogout }) {
  const [activeView, setActiveView] = useState('accounts'); // Default to the new Accounts page

  const renderView = () => {
    switch (activeView) {
      case 'brand-voices':
        return <BrandVoiceManager user={user} />;
      case 'social-media':
        return <SocialMediaManager user={user} />;
      case 'accounts': // Add the new case for accounts
        return <AccountManager user={user} />;
      default:
        return <AccountManager user={user} />; // Default to accounts view
    }
  };

  return (
    <div className={styles.dashboard}>
      <nav className={styles.sidebar}>
        <h1 className={styles.logo}>Real Estate AI</h1>
        <ul>
          {/* Add the new "Accounts" button */}
          <li 
            className={activeView === 'accounts' ? styles.active : ''}
            onClick={() => setActiveView('accounts')}
          >
            Accounts
          </li>
          <li 
            className={activeView === 'brand-voices' ? styles.active : ''}
            onClick={() => setActiveView('brand-voices')}
          >
            Brand Voices
          </li>
          <li 
            className={activeView === 'social-media' ? styles.active : ''}
            onClick={() => setActiveView('social-media')}
          >
            Social Media Posts
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
        {renderView()}
      </main>
    </div>
  );
}

export default Dashboard;
