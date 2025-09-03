import React from 'react';
import styles from './Dashboard.module.css';
import BrandVoiceManager from './BrandVoiceManager'; // We will create this next

// This component will hold the main layout of the logged-in experience
function Dashboard({ user, onLogout }) {
  return (
    <div className={styles.dashboard}>
      <nav className={styles.sidebar}>
        <h2 className={styles.sidebarTitle}>Real Estate AI</h2>
        <ul>
          <li className={styles.active}>Brand Voices</li>
          <li>Social Media Posts</li>
          <li>SEO Tools</li>
          <li>A/B Testing</li>
          {/* Add other navigation items here */}
        </ul>
        <div className={styles.userProfile}>
          <span>{user.username}</span>
          <button onClick={onLogout} className={styles.logoutButton}>Logout</button>
        </div>
      </nav>
      <main className={styles.mainContent}>
        <header className={styles.mainHeader}>
          <h1>Brand & Content Generation</h1>
        </header>
        <div className={styles.contentArea}>
          {/* The BrandVoiceManager component will handle all brand voice logic */}
          <BrandVoiceManager user={user} />
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
