import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

// You can define your navigation links here
const navigation = [
  { name: 'Accounts', href: '/accounts' },
  { name: 'Brand Voices', href: '/brand-voices' },
  { name: 'Social Media Posts', href: '/social-media' },
  { name: 'Market Analysis', href: '/market-analysis' },
  { name: 'SEO Tools', href: '/seo-tools', disabled: true },
  { name: 'A/B Testing', href: '/ab-testing', disabled: true },
];

// This is a helper component for the navigation links to handle styling
function NavItem({ item }) {
  const baseClasses = "group flex items-center px-3 py-2 text-sm font-medium rounded-md";
  const activeClasses = "bg-gray-900 text-white";
  const inactiveClasses = "text-gray-300 hover:bg-gray-700 hover:text-white";
  const disabledClasses = "text-gray-500 cursor-not-allowed";

  if (item.disabled) {
    return (
      <span className={`${baseClasses} ${disabledClasses}`} title="Coming Soon">
        {item.name}
      </span>
    );
  }

  return (
    <NavLink
      to={item.href}
      className={({ isActive }) => `${baseClasses} ${isActive ? activeClasses : inactiveClasses}`}
    >
      {item.name}
    </NavLink>
  );
}

function DashboardLayout({ user, onLogout }) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Static sidebar for desktop */}
      <div className="flex flex-shrink-0">
        <div className="flex w-64 flex-col bg-gray-800">
          <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
            <div className="flex flex-shrink-0 items-center px-4">
              <h1 className="text-2xl font-bold text-white">Real Estate AI</h1>
            </div>
            <nav className="mt-5 flex-1 space-y-1 px-2">
              {navigation.map((item) => (
                <NavItem key={item.name} item={item} />
              ))}
            </nav>
          </div>
          <div className="flex flex-shrink-0 border-t border-gray-700 p-4">
            <div className="flex w-full items-center justify-between">
                <span className="text-sm font-medium text-white">{user.username}</span>
                <button
                  onClick={onLogout}
                  className="ml-3 inline-flex items-center justify-center rounded-md bg-red-600 px-3 py-1 text-sm font-medium text-white shadow-sm hover:bg-red-700"
                >
                  Logout
                </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content area */}
      <main className="flex-1 overflow-y-auto bg-gray-200 p-8">
        {/* The Outlet is where the different pages will be rendered */}
        <Outlet />
      </main>
    </div>
  );
}

export default DashboardLayout;
