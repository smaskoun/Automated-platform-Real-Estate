import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Megaphone,
  Search,
  Share2,
  Users,
} from 'lucide-react';

// You can define your navigation links here
const navigation = [
  { name: 'Accounts', href: '/accounts', icon: Users },
  { name: 'Brand Voices', href: '/brand-voices', icon: Megaphone },
  { name: 'Social Media Posts', href: '/social-media', icon: Share2 },
  { name: 'SEO Tools', href: '/seo-tools', icon: Search },
];

// This is a helper component for the navigation links to handle styling
function NavItem({ item }) {
  const baseClasses = "group flex items-center gap-3 px-3 py-3 text-sm font-medium rounded-lg";
  const activeClasses = "bg-gray-800 text-primary-400";
  const inactiveClasses = "text-gray-300 hover:bg-gray-800 hover:text-white";
  const disabledClasses = "text-gray-500 cursor-not-allowed";
  const Icon = item.icon;

  if (item.disabled) {
    return (
      <span className={`${baseClasses} ${disabledClasses}`} title="Coming Soon">
        {Icon ? <Icon className="h-5 w-5" aria-hidden="true" /> : null}
        <span>{item.name}</span>
      </span>
    );
  }

  return (
    <NavLink
      to={item.href}
      className={({ isActive }) => `${baseClasses} ${isActive ? activeClasses : inactiveClasses}`}
    >
      {Icon ? <Icon className="h-5 w-5" aria-hidden="true" /> : null}
      <span>{item.name}</span>
    </NavLink>
  );
}

function DashboardLayout({ user, onLogout }) {
  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Static sidebar for desktop */}
      <aside className="bg-gray-900 text-white w-64 min-h-screen p-4 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 bg-primary-600 rounded-lg">
            <LayoutDashboard className="h-5 w-5" aria-hidden="true" />
          </div>
          <h1 className="text-xl font-semibold">Real Estate AI</h1>
        </div>

        <nav className="flex-1 flex flex-col gap-1">
          {navigation.map((item) => (
            <NavItem key={item.name} item={item} />
          ))}
        </nav>

        <div className="border-t border-gray-800 pt-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-white">{user.username}</span>
            <button
              onClick={onLogout}
              className="inline-flex items-center justify-center rounded-md bg-red-600 px-3 py-1 text-sm font-medium text-white shadow-sm hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <main className="flex-1 overflow-y-auto bg-gray-200 p-8">
        {/* The Outlet is where the different pages will be rendered */}
        <Outlet />
      </main>
    </div>
  );
}

export default DashboardLayout;
