'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { BackendStatus } from '@/components/ui/BackendStatus';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Sidebar />
      <main className="flex-1 ml-64 p-8">
        <BackendStatus />
        {children}
      </main>
    </div>
  );
};