import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  Building2,
  LayoutDashboard,
  Megaphone,
  Menu,
  Search,
  Share2,
  Users,
  X,
} from 'lucide-react';

const navigation = [
  { name: 'Accounts', href: '/accounts', icon: Users },
  { name: 'Properties', href: '/properties', icon: Building2 },
  { name: 'Brand Voices', href: '/brand-voices', icon: Megaphone },
  { name: 'Social Media Posts', href: '/social-media', icon: Share2 },
  { name: 'SEO Tools', href: '/seo-tools', icon: Search },
];

function NavItem({ item, onNavigate }) {
  const Icon = item.icon;

  if (item.disabled) {
    return (
      <span className="nav-item disabled" title="Coming Soon">
        {Icon ? <Icon className="nav-icon" aria-hidden="true" /> : null}
        <span>{item.name}</span>
      </span>
    );
  }

  return (
    <NavLink
      to={item.href}
      className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
      onClick={onNavigate}
    >
      {Icon ? <Icon className="nav-icon" aria-hidden="true" /> : null}
      <span>{item.name}</span>
    </NavLink>
  );
}

function DashboardLayout({ user, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const username = user?.username ?? 'User';
  const userInitial = username.charAt(0).toUpperCase();

  const handleToggleMenu = () => {
    setMenuOpen((open) => !open);
  };

  const handleCloseMenu = () => {
    setMenuOpen(false);
  };

  return (
    <div className="dashboard-layout">
      <aside className={`sidebar${menuOpen ? ' open' : ''}`}>
        <div className="sidebar-header">
          <div className="brand">
            <span className="brand-icon">
              <LayoutDashboard aria-hidden="true" />
            </span>
            <div className="brand-name">
              <span>Control</span>
              <span>Real Estate AI</span>
            </div>
          </div>
        </div>
        <nav className="nav-section" aria-label="Primary">
          <span className="nav-label">Navigation</span>
          <ul className="nav-list">
            {navigation.map((item) => (
              <li key={item.name}>
                <NavItem item={item} onNavigate={handleCloseMenu} />
              </li>
            ))}
          </ul>
        </nav>
        <div className="sidebar-footer">
          <div className="user-card">
            <span className="avatar" aria-hidden="true">
              {userInitial}
            </span>
            <div className="user-meta">
              <span className="user-name">{username}</span>
              <span className="user-role">Administrator</span>
            </div>
          </div>
          <button type="button" className="logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </aside>
      {menuOpen ? <div className="sidebar-backdrop" onClick={handleCloseMenu} /> : null}
      <div className="main-content">
        <header className="header">
          <button
            type="button"
            className={`menu-toggle${menuOpen ? ' open' : ''}`}
            onClick={handleToggleMenu}
            aria-label={`${menuOpen ? 'Close' : 'Open'} navigation menu`}
          >
            {menuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
          </button>
          <div className="header-info">
            <h1>Welcome back, {username}</h1>
            <p>Manage your accounts, listings, and marketing automations from one hub.</p>
          </div>
          <div className="header-actions">
            <div className="profile-chip">
              <span className="avatar" aria-hidden="true">
                {userInitial}
              </span>
              <span>{username}</span>
            </div>
          </div>
        </header>
        <section className="content-area">
          <Outlet />
        </section>
      </div>
    </div>
  );
}

export default DashboardLayout;
