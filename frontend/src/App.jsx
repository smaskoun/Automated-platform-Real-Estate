import React, { useState } from 'react';
import styles from './App.module.css';
import axios from 'axios';

// CORRECTED IMPORT PATH: No './components/' folder
import Dashboard from './Dashboard.jsx';

const API_URL = import.meta.env.VITE_API_URL || 'https://your-backend-app.onrender.com';

function App( ) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [user, setUser] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post(`${API_URL}/users/login`, { email, password });
      if (response.data.success) {
        setIsLoggedIn(true);
        setUser(response.data.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please check credentials or server status.');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
  };

  if (isLoggedIn) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className={styles.loginContainer}>
      <form className={styles.loginForm} onSubmit={handleLogin}>
        <h2>Real Estate Platform Login</h2>
        <div className={styles.inputGroup}>
          <label htmlFor="email">Email</label>
          <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className={styles.inputGroup}>
          <label htmlFor="password">Password</label>
          <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        {error && <p className={styles.error}>{error}</p>}
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default App;
