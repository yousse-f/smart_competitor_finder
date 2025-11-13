'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { clsx } from 'clsx';
import { 
  LayoutDashboard, 
  Search, 
  FileText, 
  User, 
  Settings,
  LogOut,
  Globe
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Nuova Analisi', href: '/analyze', icon: Search },
  { name: 'Report', href: '/reports', icon: FileText },
  { name: 'Account', href: '/account', icon: User },
];

const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    // Logout logic (clear session, etc.)
    console.log('Logging out...');
    // Redirect to landing page
    router.push('/');
  };

  return (
    <div className="flex flex-col w-64 bg-surface border-r border-border h-screen overflow-hidden rounded-r-2xl">
      {/* Logo & Brand */}
      <div className="flex items-center px-6 py-4 border-b border-border">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
            {/* Magnifying glass solo */}
            <Search className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-text-primary">Smart Competitor</h1>
            <p className="text-xs text-text-muted">Finder</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200',
                {
                  'bg-primary-500/10 text-primary-400 border border-primary-500/20': isActive,
                  'text-text-secondary hover:text-text-primary hover:bg-surface-hover': !isActive,
                }
              )}
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="px-4 py-4 border-t border-border">
        <Link 
          href="/account"
          className="flex items-center px-3 py-2 text-sm hover:bg-surface-hover rounded-lg transition-colors duration-200 cursor-pointer"
        >
          <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center mr-3">
            <span className="text-white font-medium">F</span>
          </div>
          <div className="flex-1">
            <p className="text-text-primary font-medium">Federico</p>
            <p className="text-text-muted text-xs">Consulente</p>
          </div>
        </Link>
        
        <div className="mt-2 pt-2 border-t border-border">
          <Link 
            href="/account"
            className="flex items-center w-full px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors duration-200"
          >
            <Settings className="w-4 h-4 mr-3" />
            Impostazioni
          </Link>
          <button 
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm text-text-secondary hover:text-error hover:bg-error/10 rounded-lg transition-colors duration-200"
          >
            <LogOut className="w-4 h-4 mr-3" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export { Sidebar };